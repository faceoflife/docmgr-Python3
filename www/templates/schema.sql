-- schema.sql

drop database if exists python3_webapp;

create database python3_webapp;

use python3_webapp;

create table users (
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `passwd` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
    `created_at` real not null,
    unique key `idx_email` (`email`),  -- unique表示这是一个唯一约束列
    key `idx_created_at` (`created_at`),  -- key表示索引，用来加快查询速度的 
    primary key (`id`)
) engine=innodb default charset=utf8;

create table blogs (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `name` varchar(50) not null,
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table comments (
    `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table category (
    `id` varchar(50) not null,
    `enum` varchar(2) not null,
    `name` varchar(100) not null,
    `icon` varchar(100) not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table ebook_catalog (
    `id` varchar(50) not null,
    `tags` varchar(500) not null,
    `title` varchar(100) not null,
    `author` varchar(200) not null,
    `summary` varchar(500) not null,
    `order_seq` int(2) not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table ebook_item (
    `id` varchar(50) not null,
    `catalog_id` varchar(50) not null,
    `title` varchar(100) not null,
    `content` text not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table ebook_tags (
    `id` varchar(50) not null,
    `name` varchar(50) not null,
    `badge_type` varchar(100) not null,
    `order_seq` int(2) not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
