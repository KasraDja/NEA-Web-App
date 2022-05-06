
CREATE TABLE IF NOT EXISTS user (
        user_id VARCHAR(8) PRIMARY KEY,
        user_firstname VARCHAR(24) NOT NULL,  
        user_surname VARCHAR(24) NOT NULL,
        user_email TINYTEXT NOT NULL,
        username VARCHAR(20) NOT NULL,
        user_passSalt TEXT NOT NULL,
        user_passhash TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS subscribed_categories(
        user_id VARCHAR(8), 
        category TEXT,
        category_weight INT
    );

CREATE TABLE IF NOT EXISTS friends (
        user_id VARCHAR(8), 
        friend_id VARCHAR(8)
    );

CREATE TABLE IF NOT EXISTS friendship_reqs (
        user_id VARCHAR(8), 
        requesting_user_id VARCHAR(8)
    );

CREATE TABLE IF NOT EXISTS comments (
        comment_id INTEGER PRIMARY KEY, 
        comment_text VARCHAR(512) NOT NULL, 
        comment_likes INT,
        comment_date_created DATE,
        user_id VARCHAR(8),
        post_id VARCHAR(8)
    );

CREATE TABLE IF NOT EXISTS posts (
        post_id VARCHAR(8) PRIMARY KEY,
        post_type TINYTEXT NOT NULL,
        post_title TINYTEXT NOT NULL,
        post_image_link TEXT NOT NULL,
        post_link TEXT NOT NULL,
        post_likes INT,
        post_text LONGTEXT NOT NULL
    );

CREATE TABLE IF NOT EXISTS post_tags (
        post_id VARCHAR(8), 
        post_tag VARCHAR(32)
    );

CREATE TABLE IF NOT EXISTS saved_for_later (
        post_id VARCHAR(8), 
        user_id VARCHAR(8)
    );

CREATE TABLE IF NOT EXISTS liked_posts (
    post_id VARCHAR(8), 
    user_id VARCHAR(8)
    );

CREATE TABLE IF NOT EXISTS user_activity (
    user_id VARCHAR(8) PRIMARY KEY, 
    post_id VARCAHR(8)
    );

