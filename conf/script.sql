create table Authorized_role
(
    id   varchar(50)  not null,
    name varchar(255) not null,
    constraint table_name_id_uindex
        unique (id)
);

alter table Authorized_role
    add primary key (id);

create table Event
(
    id           int auto_increment
        primary key,
    id_message   varchar(50)          null,
    date_closure datetime             null,
    max_user     int                  null,
    users        text                 null,
    type         varchar(255)         not null,
    open         tinyint(1) default 1 null,
    constraint event_id_message_uindex
        unique (id_message)
);

create table User
(
    id   varchar(50)  not null,
    name varchar(255) null,
    constraint user_id_uindex
        unique (id)
);

alter table User
    add primary key (id);

