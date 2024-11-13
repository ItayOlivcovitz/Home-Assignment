CREATE TABLE IF NOT EXISTS counter (
                                       count INT DEFAULT 0
);

INSERT INTO counter (count) VALUES (0);

CREATE TABLE IF NOT EXISTS access_log (
                                          id INT AUTO_INCREMENT PRIMARY KEY,
                                          date DATETIME,
                                          client_ip VARCHAR(45),
    server_ip VARCHAR(45)
    );
