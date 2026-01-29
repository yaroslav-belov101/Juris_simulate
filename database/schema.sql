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

-- Триггер для обновления last_seen при любом изменении
CREATE TRIGGER IF NOT EXISTS update_last_seen 
AFTER UPDATE ON user_stats
BEGIN
    UPDATE user_stats SET last_seen = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
END;