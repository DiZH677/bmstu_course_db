--liquibase formatted sql
--changeset dmitrijzigunov:create-test-table
DROP TABLE IF EXISTS VEHICLE CASCADE;
CREATE TABLE VEHICLE
(
    id serial primary key,
    dtp_id int,
    marka_ts varchar(100),
    m_ts varchar(100),
    r_rul varchar(50),
    type_ts varchar(200),
    car_year int,
    color varchar(15),
    FOREIGN KEY(dtp_id) REFERENCES DTP(id)
);
--rollback DROP TABLE


--rollback testTable