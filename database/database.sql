CREATE DATABASE luatgiaothong;
USE luatgiaothong;
CREATE TABLE LoiViPham (
    LoiViPhamID INT AUTO_INCREMENT PRIMARY KEY,
    NoiDung TEXT NOT NULL
);
CREATE TABLE PhuongTien (
    PhuongTienID INT AUTO_INCREMENT PRIMARY KEY,
    TenPhuongTien NVARCHAR(50) NOT NULL
);
CREATE TABLE HinhPhat (
    HinhPhatID INT AUTO_INCREMENT PRIMARY KEY,
    NoiDung TEXT NOT NULL
);
CREATE TABLE ChiTietLoi (
    ChiTietLoiID INT AUTO_INCREMENT PRIMARY KEY,
    NoiDung TEXT NOT NULL
);
CREATE TABLE Luat (
    LuatID INT AUTO_INCREMENT PRIMARY KEY,
    LoiViPhamID INT,
    PhuongTienID INT,
    ChiTietLoiID INT,
    HinhPhatID INT,
    DieuKhoan  NVARCHAR(255) NOT NULL,
    NgayApDung DATE,
    FOREIGN KEY (LoiViPhamID) REFERENCES loivipham(LoiViPhamID),
    FOREIGN KEY (PhuongTienID) REFERENCES PhuongTien(PhuongTienID),
    FOREIGN KEY (ChiTietLoiID) REFERENCES ChiTietLoi(ChiTietLoiID),
    FOREIGN KEY (HinhPhatID) REFERENCES HinhPhat(HinhPhatID)
);

ALTER TABLE LoiViPham
ADD CONSTRAINT unique_noidung UNIQUE (NoiDung(255));

ALTER TABLE ChiTietLoi
ADD CONSTRAINT unique_noidung UNIQUE (NoiDung(255));

ALTER TABLE HinhPhat
ADD CONSTRAINT unique_noidung UNIQUE (NoiDung(255));

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user'
);

INSERT INTO users (username, password, role) VALUES ('admin', 'adminpassword','admin');
INSERT INTO users (username, password) VALUES ('user1', '1234');