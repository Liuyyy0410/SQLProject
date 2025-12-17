CREATE DATABASE IF NOT EXISTS db_theatre;
USE db_theatre;

SET foreign_key_checks=0;

-- 删除旧表
DROP TABLE IF EXISTS movie_genres;
DROP TABLE IF EXISTS booked_tickets;
DROP TABLE IF EXISTS shows;
DROP TABLE IF EXISTS price_listing;
DROP TABLE IF EXISTS hall_seats;
DROP TABLE IF EXISTS halls;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS types;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS snack_sales;
DROP TABLE IF EXISTS snacks;

-- 1. 影厅表
CREATE TABLE halls (
    hall_id INT PRIMARY KEY
);

-- 2. 影厅座位配置
CREATE TABLE hall_seats (
    hall_id INT,
    class VARCHAR(10),
    total_seats INT, 
    PRIMARY KEY(hall_id, class),
    FOREIGN KEY(hall_id) REFERENCES halls(hall_id) ON DELETE CASCADE
);

-- 3. 电影表
CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    movie_name VARCHAR(100),
    length INT,
    language VARCHAR(20),
    show_start DATE,
    show_end DATE
);

-- 4. 电影题材 
CREATE TABLE movie_genres (
    movie_id INT,
    genre VARCHAR(20),
    PRIMARY KEY(movie_id, genre),
    FOREIGN KEY(movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
);

-- 5. 价目表
CREATE TABLE price_listing (
    price_id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(10), 
    day VARCHAR(10),
    price INT,
    UNIQUE KEY(type, day)
);

-- 6. 排片表 
CREATE TABLE shows (
    show_id INT PRIMARY KEY,
    movie_id INT,
    hall_id INT,
    type VARCHAR(10),
    time INT,
    show_date DATE,
    FOREIGN KEY(movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY(hall_id) REFERENCES halls(hall_id) ON DELETE CASCADE
);

-- 7. 会员表
CREATE TABLE members (
    member_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    phone VARCHAR(20) UNIQUE,
    points INT DEFAULT 0
);

-- 8. 订单表 (触发器将监听此表)
CREATE TABLE booked_tickets (
    ticket_no INT PRIMARY KEY,
    show_id INT,
    seat_no INT,
    member_id INT, 
    FOREIGN KEY(show_id) REFERENCES shows(show_id) ON DELETE CASCADE,
    FOREIGN KEY(member_id) REFERENCES members(member_id) ON DELETE SET NULL
);

-- 9. 小吃表
CREATE TABLE snacks (
    snack_id INT PRIMARY KEY AUTO_INCREMENT,
    snack_name VARCHAR(50),
    price INT
);

-- 10. 小吃销售记录
CREATE TABLE snack_sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    snack_id INT,
    quantity INT,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(snack_id) REFERENCES snacks(snack_id) ON DELETE CASCADE
);

SET foreign_key_checks=1;

-- 初始化数据
INSERT INTO halls VALUES (1), (2), (3);

INSERT INTO hall_seats VALUES
(1, "gold", 35), (1, "standard", 75), 
(2, "gold", 27), (2, "standard", 97), 
(3, "gold", 26), (3, "standard", 98);

INSERT INTO price_listing (type, day, price) VALUES
('2D', 'Monday', 30), ('3D', 'Monday', 45), ('4DX', 'Monday', 60),
('2D', 'Tuesday', 30), ('3D', 'Tuesday', 45), ('4DX', 'Tuesday', 60),
('2D', 'Wednesday', 30), ('3D', 'Wednesday', 45), ('4DX', 'Wednesday', 60),
('2D', 'Thursday', 30), ('3D', 'Thursday', 45), ('4DX', 'Thursday', 60),
('2D', 'Friday', 50), ('3D', 'Friday', 65), ('4DX', 'Friday', 90),
('2D', 'Saturday', 60), ('3D', 'Saturday', 75), ('4DX', 'Saturday', 100),
('2D', 'Sunday', 60), ('3D', 'Sunday', 75), ('4DX', 'Sunday', 100);

-- 电影数据
INSERT INTO movies VALUES (101, '阿凡达：火与灰 (Avatar: Fire and Ash)', 190, '英语', '2025-12-19', '2026-02-28');
INSERT INTO movie_genres VALUES (101, '动作'), (101, '奇幻'), (101, '科幻');
INSERT INTO movies VALUES (102, '海绵宝宝：寻找方裤裤', 95, '英语/国语', '2025-12-19', '2026-01-30');
INSERT INTO movie_genres VALUES (102, '动画'), (102, '喜剧'), (102, '家庭');
INSERT INTO movies VALUES (103, '女佣 (The Housemaid)', 110, '英语', '2025-12-19', '2026-01-20');
INSERT INTO movie_genres VALUES (103, '惊悚'), (103, '悬疑'), (103, '剧情');
INSERT INTO movies VALUES (104, '大卫王 (David)', 100, '英语', '2025-12-19', '2026-01-15');
INSERT INTO movie_genres VALUES (104, '动画'), (104, '历史'), (104, '音乐');
INSERT INTO movies VALUES (105, '这玩意儿开着吗?', 105, '英语', '2025-12-19', '2026-01-15');
INSERT INTO movie_genres VALUES (105, '喜剧'), (105, '剧情'), (105, '独立');
INSERT INTO movies VALUES (106, '马蒂至尊 (Marty Supreme)', 125, '英语', '2025-12-25', '2026-02-10');
INSERT INTO movie_genres VALUES (106, '剧情'), (106, '运动'), (106, '传记');
INSERT INTO movies VALUES (107, '蓝色歌唱 (Song Sung Blue)', 115, '英语', '2025-12-25', '2026-01-30');
INSERT INTO movie_genres VALUES (107, '音乐'), (107, '爱情'), (107, '剧情');
INSERT INTO movies VALUES (108, '狂蟒之灾：重生', 100, '英语', '2025-12-25', '2026-01-25');
INSERT INTO movie_genres VALUES (108, '恐怖'), (108, '动作'), (108, '惊悚');
INSERT INTO movies VALUES (109, '末日大洪水 (The Great Flood)', 130, '英语', '2025-12-25', '2026-01-30');
INSERT INTO movie_genres VALUES (109, '灾难'), (109, '科幻'), (109, '动作');
INSERT INTO movies VALUES (110, '六月再见 (Goodbye June)', 105, '英语', '2025-12-20', '2026-01-10');
INSERT INTO movie_genres VALUES (110, '家庭'), (110, '剧情'), (110, '节日');

-- 排片数据
INSERT INTO shows (show_id, movie_id, hall_id, type, time, show_date) VALUES 
(1001, 101, 1, '3D', 1000, '2025-12-25'),
(1002, 101, 1, '4DX', 1400, '2025-12-25'),
(1003, 106, 2, '2D', 1830, '2025-12-25'),
(1004, 108, 3, '2D', 2100, '2025-12-25'),
(1005, 102, 2, '2D', 1000, '2025-12-26'),
(1006, 103, 3, '2D', 2100, '2025-12-26'),
(1007, 104, 1, '2D', 1300, '2025-12-26'),
(1008, 105, 2, '2D', 1900, '2025-12-26'),
(1009, 107, 3, '2D', 1600, '2025-12-26'),
(1010, 109, 1, '3D', 1400, '2025-12-26'),
(1011, 110, 2, '2D', 1800, '2025-12-26');

INSERT INTO snacks (snack_name, price) VALUES 
('爆米花 (Popcorn)', 20), 
('可乐 (Coke)', 10), 
('薯片 (Chips)', 15),
('矿泉水 (Water)', 5);

-- =======================================
-- 核心功能：使用触发器代替应用层逻辑
-- =======================================

-- 1. 存储过程：清理旧数据
DROP PROCEDURE IF EXISTS delete_old;
DELIMITER //
CREATE PROCEDURE delete_old()
BEGIN
    DELETE FROM shows WHERE show_date < CURDATE();
END; //
DELIMITER ;

-- 2. 触发器：会员积分自动累计
-- 当booked_tickets表插入新记录后，自动触发
DROP TRIGGER IF EXISTS trigger_add_points;
DELIMITER //
CREATE TRIGGER trigger_add_points
AFTER INSERT ON booked_tickets
FOR EACH ROW
BEGIN
    -- 只有当订单关联了会员(member_id不为空)时，才增加积分
    IF NEW.member_id IS NOT NULL THEN
        UPDATE members 
        SET points = points + 10 
        WHERE member_id = NEW.member_id;
    END IF;
END; //
DELIMITER ;
