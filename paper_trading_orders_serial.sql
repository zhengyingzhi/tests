/*
 Navicat Premium Data Transfer

 Source Server         : 136paper
 Source Server Type    : PostgreSQL
 Source Server Version : 90515
 Source Host           : 192.168.1.136:5432
 Source Catalog        : papertrading
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 90515
 File Encoding         : 65001

 Date: 23/02/2019 11:24:29
*/


CREATE SEQUENCE paper_trading_orders_serial_id_seq
	INCREMENT 1
	START 1
	MINVALUE 1
	MAXVALUE 999999999
	CACHE 1;

ALTER SEQUENCE paper_trading_orders_serial_id_seq OWNER TO papertrading;


-- ----------------------------
-- Table structure for paper_trading_orders_serial
-- ----------------------------
DROP TABLE IF EXISTS "public"."paper_trading_orders_serial";
CREATE TABLE "public"."paper_trading_orders_serial" (
  "id" int4 NOT NULL DEFAULT nextval('paper_trading_orders_serial_id_seq'::regclass),
  "account" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "acct_type" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "run_date" date NOT NULL,
  "symbol" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "order_qty" int4 NOT NULL,
  "order_price" float8 NOT NULL,
  "trade_side" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "order_type" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "order_param" varchar(200) COLLATE "pg_catalog"."default",
  "order_no" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "filled_qty" int4 NOT NULL,
  "avg_price" float8 NOT NULL,
  "cancel_qty" int4,
  "order_time" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "status" int4 NOT NULL,
  "corr_type" varchar(30) COLLATE "pg_catalog"."default",
  "corr_id" varchar(200) COLLATE "pg_catalog"."default",
  "extensions" text COLLATE "pg_catalog"."default" DEFAULT ''::text,
  "fare" float8,
  "stock_name" varchar(30) COLLATE "pg_catalog"."default"
)
;

-- ----------------------------
-- Primary Key structure for table paper_trading_orders_serial
-- ----------------------------
ALTER TABLE "public"."paper_trading_orders_serial" ADD CONSTRAINT "paper_trading_orders_serial_pkey" PRIMARY KEY ("id");
