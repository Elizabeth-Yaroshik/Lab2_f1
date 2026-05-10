-- Вставка пилотов (без указания pilot_id – счётчик сам назначит значения)
INSERT INTO Pilots (full_name, birth_date, car_number, comment) VALUES
('Макс Ферстаппен', '1997-09-30', 3, 'Четырёхкратный чемпион мира'),
('Льюис Хэмилтон', '1985-01-07', 44, 'Семикратный чемпион мира'),
('Ландо Норрис', '1999-11-13', 1, 'Действующий чемпион мира');

-- Вставка результатов гонок (pilot_id ссылается на автоматически сгенерированные ID пилотов)
INSERT INTO RaceResults (pilot_id, race_name, race_date, position, time_seconds) VALUES
((SELECT pilot_id FROM Pilots WHERE full_name = 'Макс Ферстаппен'), 'Гран-при Майами', '2026-05-03', 5, 5643,222),
((SELECT pilot_id FROM Pilots WHERE full_name = 'Льюис Хэмилтон'), 'Гран-при Майами', '2026-05-03', 6, 5653.026),
((SELECT pilot_id FROM Pilots WHERE full_name = 'Макс Ферстаппен'), 'Гран-при Японии', '2026-03-29', 8, 5316.08),
((SELECT pilot_id FROM Pilots WHERE full_name = 'Ландо Норрис'), 'Гран-при Японии', '2026-03-29', 5, 5306.882);
