CREATE TABLE IF NOT EXISTS vessel_positions (
  vessel_name text,
  company text,
  lat double precision,
  lon double precision,
  sog double precision,
  heading double precision,
  destination text,
  eta date
);

INSERT INTO vessel_positions VALUES
('Berlin Express','Hapag-Lloyd',51.95,4.15,14.8,91,'Singapore','2026-06-04'),
('Hamburg Express','Hapag-Lloyd',31.25,32.31,12.1,128,'Jebel Ali','2026-05-30'),
('Al Nefud','Hapag-Lloyd',1.29,103.84,9.6,270,'Shanghai','2026-06-02'),
('Leverkusen Express','Hapag-Lloyd',53.54,9.96,0.2,180,'Rotterdam','2026-05-27'),
('OceanTwin Demo Vessel','Demo Line',37.94,23.65,16.4,111,'Port Said','2026-05-29');

CREATE TABLE IF NOT EXISTS operational_events (
  event_time timestamp,
  vessel_name text,
  event_type text,
  severity text,
  port text,
  delay_hours double precision,
  cost_usd double precision,
  co2_delta_tonnes double precision
);

INSERT INTO operational_events VALUES
('2026-05-20 08:00','Berlin Express','Port congestion','High','Rotterdam',18,42000,55),
('2026-05-20 14:30','Hamburg Express','Weather deviation','Medium','Port Said',7,18000,32),
('2026-05-21 10:15','Al Nefud','Slow steaming','Low','Singapore',-4,-9000,-48),
('2026-05-21 18:45','Leverkusen Express','Berth waiting','Medium','Hamburg',11,25000,21),
('2026-05-22 09:20','Berlin Express','Terminal delay','High','Antwerp',16,38000,44),
('2026-05-23 05:50','Hamburg Express','Canal queue','High','Port Said',20,51000,72),
('2026-05-24 11:40','Al Nefud','Port congestion','High','Shanghai',22,61000,87);
