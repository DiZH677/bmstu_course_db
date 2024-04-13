--liquibase formatted sql
--changeset dmitrijzigunov:create-test-table
DROP TABLE IF EXISTS DTP CASCADE;
CREATE TABLE DTP
(
    id          serial primary key,
    description varchar(100),
    datetime    timestamp,
    coord_w     float,
    coord_l     float,
    dor         varchar(200),
    osv         varchar(50),
    count_ts    int,
    count_parts int
);
--rollback DROP TABLE

--changeset dmitrijzigunov:add-field
ALTER TABLE dtp ADD COLUMN test varchar(15);

--changeset dmitrijzigunov:del-field
ALTER TABLE dtp DROP COLUMN test;

--changeset dmitrijzigunov:add-field-v2
ALTER TABLE dtp ADD COLUMN test2 varchar(3);


--rollback testTable
