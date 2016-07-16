DROP TABLE IF EXISTS books;
CREATE TABLE books (
  id serial PRIMARY KEY,
  title varchar(80),
  author varchar(80),
  isbn varchar(80),
  price float
);
