DROP TABLE IF EXISTS vessel_positions;
DROP TABLE IF EXISTS operational_events;
DROP TABLE IF EXISTS route_scenarios;
DROP TABLE IF EXISTS port_risk_index;

CREATE TABLE vessel_positions (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    vessel_name TEXT NOT NULL,
    company TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    sog DOUBLE PRECISION NOT NULL,
    heading DOUBLE PRECISION NOT NULL,
    destination TEXT,
    eta TIMESTAMP,
    imo TEXT,
    mmsi TEXT,
    risk_label TEXT,
    risk_score DOUBLE PRECISION,
    carbon_tco2 DOUBLE PRECISION,
    eu_exposure BOOLEAN
);

CREATE TABLE operational_events (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    vessel_name TEXT NOT NULL,
    company TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    port TEXT NOT NULL,
    delay_hours DOUBLE PRECISION NOT NULL,
    cost_usd DOUBLE PRECISION NOT NULL,
    co2_delta_tonnes DOUBLE PRECISION NOT NULL
);

CREATE TABLE route_scenarios (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    route TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    distance_nm DOUBLE PRECISION NOT NULL,
    eta_days DOUBLE PRECISION NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    risk_label TEXT NOT NULL,
    carbon_tco2 DOUBLE PRECISION NOT NULL,
    eu_exposure BOOLEAN NOT NULL
);

CREATE TABLE port_risk_index (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    port TEXT NOT NULL,
    country TEXT NOT NULL,
    congestion_score DOUBLE PRECISION NOT NULL,
    waiting_vessels INTEGER NOT NULL,
    avg_wait_hours DOUBLE PRECISION NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    risk_label TEXT NOT NULL
);

INSERT INTO vessel_positions
(event_time, vessel_name, company, lat, lon, sog, heading, destination, eta, imo, mmsi, risk_label, risk_score, carbon_tco2, eu_exposure)
VALUES
(NOW() - interval '10 minutes','Berlin Express','Hapag-Lloyd',51.95,4.15,14.8,91,'Singapore',NOW()+interval '9 days','9495000','218123000','High',0.78,1198,true),
(NOW() - interval '8 minutes','Hamburg Express','Hapag-Lloyd',31.25,32.31,12.1,128,'Jebel Ali',NOW()+interval '4 days','9461059','218456000','Medium',0.58,820,true),
(NOW() - interval '6 minutes','Al Nefud','Hapag-Lloyd',1.29,103.84,9.6,270,'Shanghai',NOW()+interval '7 days','9708813','538004000','High',0.73,1042,false),
(NOW() - interval '5 minutes','Leverkusen Express','Hapag-Lloyd',53.54,9.96,0.2,180,'Rotterdam',NOW()+interval '2 days','9613004','218789000','Low',0.31,210,true),
(NOW() - interval '4 minutes','OceanTwin Demo Vessel','Demo Line',37.90,23.70,16.4,111,'Port Said',NOW()+interval '3 days','0000000','000000000','Medium',0.52,650,false);

INSERT INTO operational_events
(event_time, vessel_name, company, event_type, severity, port, delay_hours, cost_usd, co2_delta_tonnes)
VALUES
(NOW() - interval '6 days','Berlin Express','Hapag-Lloyd','Port congestion','High','Rotterdam',18,52000,72),
(NOW() - interval '5 days 8 hours','Hamburg Express','Hapag-Lloyd','Weather deviation','Medium','Antwerp',7,18000,31),
(NOW() - interval '4 days 20 hours','Leverkusen Express','Hapag-Lloyd','Slow steaming','Low','Singapore',-4,-9000,-48),
(NOW() - interval '4 days','Berlin Express','Hapag-Lloyd','Berth waiting','Medium','Hamburg',11,25000,21),
(NOW() - interval '3 days 12 hours','Al Nefud','Hapag-Lloyd','Terminal delay','High','Shanghai',16,61000,87),
(NOW() - interval '3 days','Hamburg Express','Hapag-Lloyd','Schedule recovery','Low','Singapore',-6,-12000,-39),
(NOW() - interval '2 days 8 hours','Berlin Express','Hapag-Lloyd','Canal queue','High','Port Said',20,69000,104),
(NOW() - interval '1 day 4 hours','Al Nefud','Hapag-Lloyd','Port congestion','High','Shanghai',22,61000,87),
(NOW() - interval '22 hours','OceanTwin Demo Vessel','Demo Line','Custom hold','Medium','Port Said',9,22000,42);

INSERT INTO route_scenarios
(event_time, route, origin, destination, distance_nm, eta_days, risk_score, risk_label, carbon_tco2, eu_exposure)
VALUES
(NOW(),'Hamburg → Singapore','Hamburg','Singapore',5480,14.3,0.78,'High',1198,true),
(NOW(),'Rotterdam → Singapore','Rotterdam','Singapore',5700,14.8,0.82,'High',1247,true),
(NOW(),'Hamburg → Shanghai','Hamburg','Shanghai',4602,12.0,0.75,'High',1007,true),
(NOW(),'Rotterdam → Shanghai','Rotterdam','Shanghai',4829,12.6,0.79,'High',1056,true),
(NOW(),'Singapore → Shanghai','Singapore','Shanghai',2060,5.4,0.52,'Medium',450,false),
(NOW(),'Hamburg → Jebel Ali','Hamburg','Jebel Ali',3180,8.3,0.61,'Medium',695,true),
(NOW(),'Shanghai → Los Angeles','Shanghai','Los Angeles',5700,14.8,0.69,'Medium',1220,false),
(NOW(),'Rotterdam → Los Angeles','Rotterdam','Los Angeles',4842,12.6,0.76,'High',1059,true);

INSERT INTO port_risk_index
(event_time, port, country, congestion_score, waiting_vessels, avg_wait_hours, risk_score, risk_label)
VALUES
(NOW(),'Shanghai','China',0.82,31,28,0.86,'High'),
(NOW(),'Rotterdam','Netherlands',0.67,18,16,0.72,'High'),
(NOW(),'Singapore','Singapore',0.76,26,21,0.81,'High'),
(NOW(),'Hamburg','Germany',0.62,14,12,0.65,'Medium'),
(NOW(),'Port Said','Egypt',0.58,11,10,0.61,'Medium'),
(NOW(),'Jebel Ali','UAE',0.43,7,6,0.44,'Low');