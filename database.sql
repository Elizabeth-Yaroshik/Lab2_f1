PRAGMA foreign_keys = ON;

CREATE TABLE Pilots (
    pilot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    birth_date TEXT NOT NULL, 
    car_number INTEGER CHECK (car_number BETWEEN 1 AND 99),
    comment TEXT
);

CREATE TABLE RaceResults (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pilot_id INTEGER NOT NULL,
    race_name TEXT NOT NULL,
    race_date TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    time_seconds REAL NOT NULL, 
    FOREIGN KEY (pilot_id) REFERENCES Pilots(pilot_id) ON DELETE RESTRICT
);
