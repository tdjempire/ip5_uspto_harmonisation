# USPTO Harmonisation Code (de Rassenfosse et. al.)

This code was written in Python 2 2015-2016 and ported to Python 3 in 2020.

The order of run is:
 * load_uspto_2020.py
 * 2020_uspto_attorney_harmonisation.py
 * makedictmysql.py
 * vectorisemysql.py
 * cosine_distance_fast_multi.py
 * uspto_match_close.py
 * uspto_code.py 
 * dump_us.py 
 
The tables in the database are as described below:

```
MariaDB> describe ip5_uspto_pat_agent_raw;
+-------------+--------------+------+-----+---------+-------+
| Field       | Type         | Null | Key | Default | Extra |
+-------------+--------------+------+-----+---------+-------+
| appln_id    | int(11)      | YES  | MUL | NULL    |       |
| appln_nr    | int(11)      | NO   | MUL | NULL    |       |
| name        | varchar(300) | YES  | MUL | NULL    |       |
| address     | varchar(300) | YES  |     | NULL    |       |
| country     | varchar(5)   | YES  |     | NULL    |       |
| clean_name  | varchar(300) | YES  | MUL | NULL    |       |
| tdj_id      | int(11)      | YES  |     | NULL    |       |
| has_changed | int(11)      | YES  |     | NULL    |       |
| name_1      | varchar(300) | YES  |     | NULL    |       |
| name_2      | varchar(300) | YES  |     | NULL    |       |
| add_1       | varchar(300) | YES  |     | NULL    |       |
| add_2       | varchar(300) | YES  |     | NULL    |       |
| city        | varchar(100) | YES  |     | NULL    |       |
| postcode    | varchar(100) | YES  |     | NULL    |       |
| region      | varchar(100) | YES  |     | NULL    |       |
+-------------+--------------+------+-----+---------+-------+
```
```
MariaDB> show index from ip5_uspto_pat_agent_raw;
+-------------------------+------------+----------------------------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| Table                   | Non_unique | Key_name                               | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment |
+-------------------------+------------+----------------------------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| ip5_uspto_pat_agent_raw |          1 | ip5_uspto_pat_agent_raw_appln_nr_IDX   |            1 | appln_nr    | A         |      570599 |     NULL | NULL   |      | BTREE      |         |               |
| ip5_uspto_pat_agent_raw |          1 | ip5_uspto_pat_agent_raw_clean_name_IDX |            1 | clean_name  | A         |           3 |     NULL | NULL   | YES  | BTREE      |         |               |
| ip5_uspto_pat_agent_raw |          1 | ip5_uspto_pat_agent_raw_name_IDX       |            1 | name        | A         |           3 |     NULL | NULL   | YES  | BTREE      |         |               |
| ip5_uspto_pat_agent_raw |          1 | ip5_uspto_pat_agent_raw_appln_id_IDX   |            1 | appln_id    | A         |      570599 |     NULL | NULL   | YES  | BTREE      |         |               |
+-------------------------+------------+----------------------------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
```

```
MariaDB> describe ip5_uspto_pat_agent_clean ;
+----------------+--------------+------+-----+---------+-------+
| Field          | Type         | Null | Key | Default | Extra |
+----------------+--------------+------+-----+---------+-------+
| appln_id       | int(11)      | NO   | PRI | NULL    |       |
| is_firm        | int(11)      | YES  |     | NULL    |       |
| recovered_firm | varchar(250) | YES  | MUL | NULL    |       |
| vector         | blob         | YES  |     | NULL    |       |
| address_clean  | varchar(500) | YES  |     | NULL    |       |
+----------------+--------------+------+-----+---------+-------+
```
```
MariaDB> show index from ip5_uspto_pat_agent_clean;
+---------------------------+------------+----------------------------------------+--------------+----------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| Table                     | Non_unique | Key_name                               | Seq_in_index | Column_name    | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment |
+---------------------------+------------+----------------------------------------+--------------+----------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| ip5_uspto_pat_agent_clean |          0 | PRIMARY                                |            1 | appln_id       | A         |      574259 |     NULL | NULL   |      | BTREE      |         |               |
| ip5_uspto_pat_agent_clean |          1 | recovered_firm_in                      |            1 | recovered_firm | A         |       38283 |     NULL | NULL   | YES  | BTREE      |         |               |
| ip5_uspto_pat_agent_clean |          1 | ip5_uspto_pat_agent_clean_appln_id_IDX |            1 | appln_id       | A         |      574259 |     NULL | NULL   |      | BTREE      |         |               |
+---------------------------+------------+----------------------------------------+--------------+----------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
```
```
MariaDB> describe ip5_uspto_pat_agent_clean_9;
+-----------+--------------+------+-----+---------+-------+
| Field     | Type         | Null | Key | Default | Extra |
+-----------+--------------+------+-----+---------+-------+
| appln_id  | int(11)      | NO   | PRI | NULL    |       |
| us_att_id | varchar(100) | YES  | MUL | NULL    |       |
+-----------+--------------+------+-----+---------+-------+
```
```
MariaDB> show index from ip5_uspto_pat_agent_clean_9;
+-----------------------------+------------+--------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| Table                       | Non_unique | Key_name     | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment |
+-----------------------------+------------+--------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| ip5_uspto_pat_agent_clean_9 |          0 | PRIMARY      |            1 | appln_id    | A         |      575162 |     NULL | NULL   |      | BTREE      |         |               |
| ip5_uspto_pat_agent_clean_9 |          1 | us_att_id_in |            1 | us_att_id   | A         |        9916 |     NULL | NULL   | YES  | BTREE      |         |               |
+-----------------------------+------------+--------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
```
```
MariaDB> describe ip5_uspto_pat_agent_clean_9_exp;
+-----------+--------------+------+-----+---------+-------+
| Field     | Type         | Null | Key | Default | Extra |
+-----------+--------------+------+-----+---------+-------+
| appln_id  | int(11)      | NO   | PRI | NULL    |       |
| us_att_id | varchar(100) | YES  | MUL | NULL    |       |
+-----------+--------------+------+-----+---------+-------+
```
```
MariaDB> show index from ip5_uspto_pat_agent_clean_9_exp;
+---------------------------------+------------+-----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| Table                           | Non_unique | Key_name  | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment |
+---------------------------------+------------+-----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| ip5_uspto_pat_agent_clean_9_exp |          0 | PRIMARY   |            1 | appln_id    | A         |      506476 |     NULL | NULL   |      | BTREE      |         |               |
| ip5_uspto_pat_agent_clean_9_exp |          1 | us_att_in |            1 | us_att_id   | A         |       19479 |     NULL | NULL   | YES  | BTREE      |         |               |
+---------------------------------+------------+-----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
```
