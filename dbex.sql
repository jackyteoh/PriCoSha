INSERT INTO Person VALUES ('JT', md5('JT'), 'Jacky', 'Teoh')
INSERT INTO Person VALUES ('MH', md5('MH'), 'Monjur', 'Hasan')
INSERT INTO Person VALUES ('AA', md5('AA'), 'Ann', 'Anderson')
INSERT INTO Person VALUES ('BB', md5('BB'), 'Bob', 'Baker')
INSERT INTO Person VALUES ('CC', md5('CC'), 'Cathy', 'Chang')
INSERT INTO Person VALUES ('DA', md5('DA'), 'David', 'Anderson')

INSERT INTO friendgroup VALUES ("Friends", 'JT', "Jacky's friends")
INSERT INTO member VALUES ('MH', "Friends", 'JT')
INSERT INTO member VALUES ('CC', "Friends", 'JT')
INSERT INTO member VALUES ('JT', "Friends", 'JT')

INSERT INTO friendgroup VALUES ("Best Friends", 'AA', "Ann's Best Friends")
INSERT INTO member VALUES ('MH', "Best Friends", 'AA')
INSERT INTO member VALUES ('BB', "Best Friends", 'AA')
INSERT INTO member VALUES ('AA', "Best Friends", 'AA')

INSERT INTO friendgroup VALUES ("Family", 'AA', "Ann's Family")
INSERT INTO member VALUES ('DA', "Family", 'AA')
INSERT INTO member VALUES ('AA', "Family", 'AA')

INSERT INTO content (username, timest, file_path, content_name, public) VALUES ('JT', 12:14, "C:\Users\Jacky\Desktop\Doggos.jpeg", "Doggos", "False")
INSERT INTO share VALUES (12345, "Friends", 'JT')
INSERT INTO comment VALUES (12345, 'CC', 22:35, "So cute!")
INSERT INTO comment VALUES (12345, 'MH', 23:01, ":D")

INSERT INTO content (username, timest, file_path, content_name, public) VALUES ('JT', 19:04, "C:\Users\Jacky\Desktop\Tree.jpeg", "Christmas Tree", "True")
INSERT INTO comment VALUES (12346, 'AA', 20:15, "Wow!")

INSERT INTO content (username, timest, file_path, content_name, public) VALUES ('AA', 13:13, "C:\Users\Ann\Pictures\fd1.jpeg", "Family Dinner", "False")
INSERT INTO share VALUES (12347, "Family", 'AA')
INSERT INTO tag VALUES (12347, 'AA', 'DA', 13:14, "True")
INSERT INTO comment VALUES (12347, 'DA', 14:01, "Haha what is Mom doing")
