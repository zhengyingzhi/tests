/*
 Navicat Premium Data Transfer

 Source Server         : 136
 Source Server Type    : PostgreSQL
 Source Server Version : 90515
 Source Host           : 192.168.1.136:5432
 Source Catalog        : papertrading
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 90515
 File Encoding         : 65001

 Date: 29/01/2019 08:47:05
*/

CREATE SEQUENCE paper_trading_trades_id_seq
	INCREMENT 1
	START 1
	MINVALUE 1
	MAXVALUE 999999999
	CACHE 1;

ALTER SEQUENCE paper_trading_trades_id_seq OWNER TO papertrading;

-- ----------------------------
-- Table structure for paper_trading_trades
-- ----------------------------
DROP TABLE IF EXISTS "public"."paper_trading_trades";
CREATE TABLE "public"."paper_trading_trades" (
  "id" int4 NOT NULL DEFAULT nextval('paper_trading_trades_id_seq'::regclass),
  "account" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "acct_type" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "run_date" date NOT NULL,
  "symbol" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "stock_name" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "trade_side" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "order_type" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "order_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "trade_id" int8 NOT NULL,
  "entru_no" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "order_qty" int4 NOT NULL,
  "filled_qty" int4 NOT NULL,
  "filled_price" float8 NOT NULL,
  "filled_amt" float8 NOT NULL,
  "extensions" text COLLATE "pg_catalog"."default" DEFAULT ''::text
)
;

-- ----------------------------
-- Uniques structure for table paper_trading_trades
-- ----------------------------
ALTER TABLE "public"."paper_trading_trades" ADD CONSTRAINT "paper_trading_trades_account_run_date_9032fd0f_uniq" UNIQUE ("id");

-- ----------------------------
-- Primary Key structure for table paper_trading_trades
-- ----------------------------
ALTER TABLE "public"."paper_trading_trades" ADD CONSTRAINT "paper_trading_trades_pkey" PRIMARY KEY ("id");
