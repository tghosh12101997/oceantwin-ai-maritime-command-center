DROP TABLE IF EXISTS vessel_positions;
DROP TABLE IF EXISTS operational_events;
DROP TABLE IF EXISTS port_risk;
DROP TABLE IF EXISTS route_kpis;

CREATE TABLE vessel_positions (
  vessel_name text,
  company text,
  imo text,
  mmsi text,
  vessel_class text,
  lat double precision,
  lon double precision,
  sog double precision,
  heading double precision,
  destination text,
  eta timestamp,
  risk_score double precision,
  co2_tonnes double precision,
  cargo_teu integer
);

INSERT INTO vessel_positions VALUES
('Berlin Express','Hapag-Lloyd','9622143','218123000','Container Ship',51.95,4.15,14.8,91,'Singapore','2026-06-04 02:00',68,1240,7800),
('Hamburg Express','Hapag-Lloyd','9461056','218456000','Container Ship',31.25,32.31,12.1,128,'Jebel Ali','2026-05-30 02:00',74,980,6400),
('Al Nefud','Hapag-Lloyd','9708806','229987000','Container Ship',1.29,103.84,9.6,270,'Shanghai','2026-06-02 02:00',61,1125,7100),
('Leverkusen Express','Hapag-Lloyd','9613025','218765000','Container Ship',53.54,9.96,0.2,180,'Rotterdam','2026-05-27 02:00',42,210,2800),
('Prague Express','Hapag-Lloyd','9450409','218333000','Container Ship',22.30,114.16,16.2,65,'Busan','2026-06-01 12:00',58,890,5300),
('Antwerp Express','Hapag-Lloyd','9612992','218991000','Container Ship',40.67,-74.04,13.7,43,'Hamburg','2026-06-06 08:30',66,1310,7600),
('Singapore Trader','Demo Line','9000001','999000001','Container Ship',25.27,55.29,15.4,105,'Colombo','2026-05-31 10:00',49,640,3600),
('OceanTwin Demo Vessel','Demo Line','9000002','999000002','Container Ship',37.94,23.65,16.4,111,'Port Said','2026-05-29 02:00',53,510,3100),
('Atlantic Bridge','Demo Line','9000003','999000003','Container Ship',34.05,-118.25,11.8,290,'Shanghai','2026-06-08 17:00',77,1460,8100);

CREATE TABLE operational_events (
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
('2026-05-24 11:40','Al Nefud','Port congestion','High','Shanghai',22,61000,87),
('2026-05-24 20:10','Prague Express','Berth waiting','Medium','Hong Kong',9,21000,19),
('2026-05-25 06:25','Antwerp Express','Weather deviation','Medium','New York',8,17000,27),
('2026-05-25 16:30','Atlantic Bridge','Port congestion','High','Los Angeles',26,72000,96),
('2026-05-26 08:30','Singapore Trader','Terminal delay','Medium','Jebel Ali',6,14000,18),
('2026-05-26 13:15','OceanTwin Demo Vessel','Canal queue','High','Port Said',15,39000,52);

CREATE TABLE port_risk (
  port text,
  country text,
  lat double precision,
  lon double precision,
  congestion_index double precision,
  risk_score double precision,
  avg_wait_hours double precision
);

INSERT INTO port_risk VALUES
('Rotterdam','Netherlands',51.95,4.15,72,68,18),
('Hamburg','Germany',53.54,9.96,48,42,11),
('Antwerp','Belgium',51.22,4.40,64,58,16),
('Port Said','Egypt',31.25,32.31,81,74,20),
('Singapore','Singapore',1.29,103.84,69,61,22),
('Shanghai','China',31.23,121.47,86,79,24),
('Jebel Ali','UAE',25.01,55.06,51,49,6),
('Los Angeles','USA',33.74,-118.27,89,77,26),
('New York','USA',40.67,-74.04,55,66,8),
('Hong Kong','China',22.30,114.16,57,58,9);

CREATE TABLE route_kpis (
  route text,
  origin text,
  destination text,
  distance_nm double precision,
  eta_risk double precision,
  carbon_intensity double precision,
  revenue_at_risk_usd double precision
);

INSERT INTO route_kpis VALUES
('Hamburg → Singapore','Hamburg','Singapore',8380,71,0.83,125000),
('Rotterdam → Shanghai','Rotterdam','Shanghai',10480,78,0.91,181000),
('Antwerp → New York','Antwerp','New York',3390,52,0.57,64000),
('Port Said → Jebel Ali','Port Said','Jebel Ali',3250,63,0.62,79000),
('Los Angeles → Shanghai','Los Angeles','Shanghai',5700,77,0.88,152000);
