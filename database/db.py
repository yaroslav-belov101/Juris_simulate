import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "juris_bot.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            role TEXT DEFAULT 'defender',
            correct_answers INTEGER DEFAULT 0,
            total_answers INTEGER DEFAULT 0,
            defender_correct INTEGER DEFAULT 0,
            defender_total INTEGER DEFAULT 0,
            prosecutor_correct INTEGER DEFAULT 0,
            prosecutor_total INTEGER DEFAULT 0,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def ensure_user(user_id: int, username: str = None, full_name: str = None, role: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    # Получаем текущую роль из базы
    cursor.execute("SELECT role FROM user_stats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    existing_role = row[0] if row else None
    
    # Если роль не передана, сохраняем существующую (или 'defender' по умолчанию)
    final_role = role if role is not None else (existing_role or "defender")
    
    cursor.execute("""
        INSERT INTO user_stats (
            user_id, username, full_name, role, first_seen, last_seen
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            full_name = excluded.full_name,
            role = excluded.role,
            last_seen = excluded.last_seen
    """, (user_id, username, full_name, final_role, now, now))
    conn.commit()
    conn.close()

def get_user_role(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM user_stats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else "defender"

def update_user_role(user_id: int, new_role: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE user_stats SET role = ? WHERE user_id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

def get_user_profile(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            username, full_name, role,
            correct_answers, total_answers,
            defender_correct, defender_total,
            prosecutor_correct, prosecutor_total,
            first_seen, last_seen
        FROM user_stats
        WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "username": row[0],
            "full_name": row[1],
            "role": row[2],
            "correct": row[3],
            "total": row[4],
            "defender_correct": row[5],
            "defender_total": row[6],
            "prosecutor_correct": row[7],
            "prosecutor_total": row[8],
            "first_seen": row[9],
            "last_seen": row[10]
        }
    return None

def update_user_stats(user_id: int, is_correct: bool, role: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    # Убедимся, что пользователь существует
    cursor.execute("""
        INSERT INTO user_stats (user_id, role, last_seen)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO NOTHING
    """, (user_id, role, now))
    
    # Обновляем общую статистику
    cursor.execute("""
        UPDATE user_stats 
        SET 
            correct_answers = correct_answers + ?,
            total_answers = total_answers + 1,
            last_seen = ?
        WHERE user_id = ?
    """, (1 if is_correct else 0, now, user_id))
    
    # Обновляем статистику по ролям
    if role == "defender":
        cursor.execute("""
            UPDATE user_stats
            SET defender_correct = defender_correct + ?, defender_total = defender_total + 1
            WHERE user_id = ?
        """, (1 if is_correct else 0, user_id))
    elif role == "prosecutor":
        cursor.execute("""
            UPDATE user_stats
            SET prosecutor_correct = prosecutor_correct + ?, prosecutor_total = prosecutor_total + 1
            WHERE user_id = ?
        """, (1 if is_correct else 0, user_id))
    
    conn.commit()
    conn.close()