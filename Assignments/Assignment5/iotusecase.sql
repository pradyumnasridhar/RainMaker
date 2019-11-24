-- phpMyAdmin SQL Dump
-- version 4.4.14
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Nov 08, 2017 at 02:07 AM
-- Server version: 5.6.26
-- PHP Version: 5.6.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `iotusecase`
--
CREATE DATABASE IF NOT EXISTS `iotusecase` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `iotusecase`;

-- --------------------------------------------------------

--
-- Table structure for table `sensordata`
--

CREATE TABLE IF NOT EXISTS `sensordata` (
  `seqId` int(11) NOT NULL,
  `nodeId` int(11) NOT NULL,
  `sensorId` int(11) NOT NULL,
  `dataValue` double NOT NULL,
  `RTCTimestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sensormeta`
--

CREATE TABLE IF NOT EXISTS `sensormeta` (
  `nodeId` int(11) NOT NULL,
  `nodeName` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `sensorId` int(11) NOT NULL,
  `sensorName` varchar(200) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `sensordata`
--
ALTER TABLE `sensordata`
  ADD PRIMARY KEY (`seqId`);

--
-- Indexes for table `sensormeta`
--
ALTER TABLE `sensormeta`
  ADD PRIMARY KEY (`nodeId`,`sensorId`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `sensordata`
--
ALTER TABLE `sensordata`
  MODIFY `seqId` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
