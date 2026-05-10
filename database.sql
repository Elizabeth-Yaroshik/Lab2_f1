CREATE DATABASE Formula1Racing;
\c Formula1Racing;

CREATE TABLE Pilots (
    pilot_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    birth_date DATE NOT NULL,
    car_number INTEGER CHECK (car_number BETWEEN 1 AND 99),
    comment TEXT
);

-- Поле pilot_id – внешний ключ на Pilots(pilot_id)
CREATE TABLE RaceResults (
    result_id SERIAL PRIMARY KEY,
    pilot_id INTEGER NOT NULL,
    race_name VARCHAR(200) NOT NULL,
    race_date DATE NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    time_seconds DECIMAL(10,3) NOT NULL,  -- время в секундах с фиксированной запятой
    CONSTRAINT fk_race_pilot FOREIGN KEY (pilot_id) 
        REFERENCES Pilots(pilot_id) ON DELETE RESTRICT
);
