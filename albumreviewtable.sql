-- 1. 부모 테이블 생성 (의존성 없음)
CREATE TABLE Artists
(
  artist_id  INT NOT NULL PRIMARY KEY,
  name       VARCHAR,
  debut_date DATE,
  country    VARCHAR
);

CREATE TABLE Genres
(
  genre_id   INT NOT NULL PRIMARY KEY,
  genre_name VARCHAR
);

CREATE TABLE Users
(
  user_id   INT NOT NULL PRIMARY KEY,
  nickname  VARCHAR,
  email     VARCHAR,
  join_date DATE
);

-- 2. 1차 자식 테이블 생성 (위 테이블들을 참조)
CREATE TABLE Albums
(
  album_id         INT NOT NULL PRIMARY KEY,
  artist_id        INT NOT NULL REFERENCES Artists(artist_id),
  title            VARCHAR,
  release_data     DATE,
  cover_image_path VARCHAR
);

CREATE TABLE Collections
(
  collection_id INT NOT NULL PRIMARY KEY,
  user_id       INT NOT NULL REFERENCES Users(user_id),
  title         VARCHAR,
  description   VARCHAR,
  created_at    TIMESTAMP
);

-- 3. 2차 자식 테이블 및 다대다 매핑 테이블 생성
CREATE TABLE Album_Genres
(
  genre_id INT NOT NULL REFERENCES Genres(genre_id),
  album_id INT NOT NULL REFERENCES Albums(album_id),
  PRIMARY KEY (genre_id, album_id)
);

CREATE TABLE Tracks
(
  track_id     INT NOT NULL PRIMARY KEY,
  album_id     INT NOT NULL REFERENCES Albums(album_id),
  track_number INT,
  title        VARCHAR,
  duration     INT,
  preview_url  VARCHAR
);

CREATE TABLE Reviews
(
  review_id    INT NOT NULL PRIMARY KEY,
  user_id      INT NOT NULL REFERENCES Users(user_id),
  album_id     INT NOT NULL REFERENCES Albums(album_id),
  rating       INT,
  comment_text VARCHAR,
  created_at   TIMESTAMP
);

CREATE TABLE Collection_Albums
(
  collection_id  INT NOT NULL REFERENCES Collections(collection_id),
  album_id       INT NOT NULL REFERENCES Albums(album_id),
  added_sequence INT,
  PRIMARY KEY (collection_id, album_id)
);

-- 4. 3차 자식 테이블 생성 (리뷰를 참조)
CREATE TABLE Review_Likes
(
  user_id   INT NOT NULL REFERENCES Users(user_id),
  review_id INT NOT NULL REFERENCES Reviews(review_id),
  liked_at  TIMESTAMP,
  PRIMARY KEY (user_id, review_id)
);