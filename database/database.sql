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
    DieuKhoan  NVARCHAR(100) NOT NULL,
    NgayApDung DATE,
    FOREIGN KEY (LoiViPhamID) REFERENCES loivipham(LoiViPhamID),
    FOREIGN KEY (PhuongTienID) REFERENCES PhuongTien(PhuongTienID),
    FOREIGN KEY (ChiTietLoiID) REFERENCES ChiTietLoi(ChiTietLoiID),
    FOREIGN KEY (HinhPhatID) REFERENCES HinhPhat(HinhPhatID)
);
