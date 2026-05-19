-- PostgreSQL Database Schema for Fintech Review Analytics

-- 1. Create Banks Table
CREATE TABLE IF NOT EXISTS banks (
    bank_id INT PRIMARY KEY,
    bank_name VARCHAR(255) NOT NULL,
    app_name VARCHAR(255)
);

-- 2. Create Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INT REFERENCES banks(bank_id),
    review_text TEXT,
    rating INT,
    review_date DATE,
    sentiment_label VARCHAR(50),
    sentiment_score NUMERIC(6,4),
    identified_theme VARCHAR(255),
    source VARCHAR(50)
);
