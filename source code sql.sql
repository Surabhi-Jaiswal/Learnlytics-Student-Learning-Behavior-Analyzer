-- Create the database
CREATE DATABASE student_dashboard;

-- Switch to the new database
USE student_dashboard;

-- Create a table for students_data
CREATE TABLE students_data (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    progress FLOAT NOT NULL,
    grades FLOAT NOT NULL,
    certifications INT NOT NULL,
    attendance FLOAT NOT NULL
);

-- Create a table for admin_data
CREATE TABLE admin_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monitoring_parameters JSON,
    engagement_metrics JSON
);
CREATE USER 'HimanshuSopra'@'localhost' IDENTIFIED BY 'Himanshu@1234';

GRANT ALL PRIVILEGES ON *.* TO 'HimanshuSopra'@'localhost';
FLUSH PRIVILEGES;




