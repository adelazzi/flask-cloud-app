-- Runs automatically on first MySQL container boot
-- Safe to re-run: uses IF NOT EXISTS

CREATE TABLE IF NOT EXISTS students (
    id          INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    matricule   CHAR(12)        NOT NULL UNIQUE,
    name        VARCHAR(100)    NOT NULL,
    family_name VARCHAR(100)    NOT NULL,
    mark        DECIMAL(4,2)    NOT NULL DEFAULT 0.00
                                CHECK (mark >= 0 AND mark <= 20),
    status      ENUM('success','failed') NOT NULL
                GENERATED ALWAYS AS (IF(mark >= 10, 'success', 'failed')) STORED,
    created_at  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;