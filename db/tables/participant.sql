--liquibase formatted sql
--changeset dmitrijzigunov:create-test-table
DROP TABLE IF EXISTS PARTICIPANT CASCADE;
CREATE TABLE PARTICIPANT
(
    id serial primary key,
    vehicle_id int,
    category varchar(50),
    warnings varchar(400),
    SAFETY_BELT bool,
    pol varchar(15),
    health varchar(200),
    FOREIGN KEY (vehicle_id) REFERENCES VEHICLE(id)
);
--rollback DROP TABLE

--rollback testTable