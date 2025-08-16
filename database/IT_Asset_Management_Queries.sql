-- Drop database if exists
DROP DATABASE IF EXISTS asset_management;

-- Create fresh database
CREATE DATABASE asset_management;
USE asset_management;

-- Staff Table
CREATE TABLE Staff (
    staffNumber INT PRIMARY KEY AUTO_INCREMENT,
    nationalId VARCHAR(7) NOT NULL,
    name VARCHAR(50) NOT NULL,
    department ENUM('IT', 'Support', 'HR') NOT NULL
);

-- Asset Table
CREATE TABLE Asset (
    assetNumber INT PRIMARY KEY AUTO_INCREMENT,
    assetType ENUM('Monitor', 'CPU', 'Keyboard', 'Mouse', 'Printer') NOT NULL,
    status ENUM('Assigned', 'Not Assigned', 'Discarded') NOT NULL,
    purchasedDate DATE NOT NULL,
    discardedDate DATE,
    location VARCHAR(50) DEFAULT 'Storage'
);

-- Asset Assignment Table
CREATE TABLE AssetHistory (
    assignmentId INT PRIMARY KEY AUTO_INCREMENT,
    assetNumber INT,
    staffNumber INT,
    assignedDate DATE NOT NULL,
    returnedDate DATE,
    FOREIGN KEY (assetNumber) REFERENCES Asset(assetNumber),
    FOREIGN KEY (staffNumber) REFERENCES Staff(staffNumber)
);

-- Sample Staff
INSERT INTO Staff (nationalId, name, department) VALUES
('A123456', 'Ali Ahmed', 'IT'),
('A154321', 'Mariyam Hassan', 'HR'),
('A187654', 'Ibrahim Zahir', 'Support'),
('A112233', 'Fathimath Nisha', 'IT'),
('A145566', 'Mohamed Shifan', 'Support');

-- Sample Assets
INSERT INTO Asset (assetType, status, purchasedDate, discardedDate, location) VALUES
('Monitor', 'Assigned', '2024-01-10', NULL, 'Storage'),
('CPU', 'Assigned', '2023-05-15', NULL, 'IT'),
('Printer', 'Discarded', '2020-02-20', '2024-07-10', NULL),
('Keyboard', 'Assigned', '2024-03-12', NULL, 'HR'),
('Mouse', 'Not Assigned', '2023-11-05', NULL, 'Storage');

-- Sample Assignments
INSERT INTO AssetHistory (assetNumber, staffNumber, assignedDate, returnedDate) VALUES
(2, 1, '2023-05-16', NULL),              -- CPU currently with Ali Ahmed
(4, 2, '2024-03-15', NULL),              -- Keyboard currently with Mariyam
(1, 3, '2024-01-20', '2024-04-01'),      -- Monitor was with Ibrahim, returned
(5, 4, '2024-04-10', '2024-05-05'),      -- Mouse was with Nisha, returned
(1, 5, '2024-06-01', NULL);              -- Monitor currently with Shifan

