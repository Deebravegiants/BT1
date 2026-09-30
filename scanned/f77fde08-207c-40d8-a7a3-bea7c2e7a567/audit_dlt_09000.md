# [?] fixed TransferAsset SQL overflow

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2019-07-03
Source: https://github.com/hyperledger-iroha/iroha/commit/cd3af636bff40a45c873b02c59318f5c88c48990
Type: security-commit

## Details
fixed TransferAsset SQL overflow

Signed-off-by: Mikhail Boldyrev <miboldyrev@gmail.com>

## Patch
### irohad/ametsuchi/impl/postgres_command_executor.cpp
```diff
@@ -433,9 +433,7 @@ namespace iroha {
                   INSERT INTO account_has_asset(account_id, asset_id, amount)
                   (
                       SELECT $1, $2, value FROM new_quantity
-                      WHERE
-                        (SELECT bool_and(checks.result) FROM checks)
-                        %s
+                      WHERE (SELECT bool_and(checks.result) FROM checks) %s
                   )
                   ON CONFLICT (account_id, asset_id) DO UPDATE
                   SET amount = EXCLUDED.amount
@@ -782,84 +780,69 @@ namespace iroha {
           PREPARE %s (text, text, text, text, int, text) AS
           WITH
               %s
-              has_src_account AS (SELECT account_id FROM account
-                                   WHERE account_id = $2 LIMIT 1),
-              has_dest_account AS (SELECT account_id FROM account
-                                    WHERE account_id = $3
-                                    LIMIT 1),
-              has_asset AS (SELECT asset_id FROM asset
-                             WHERE asset_id = $4 AND
-                             precision >= $5 LIMIT 1),
-              src_amount AS (SELECT amount FROM account_has_asset
-                              WHERE asset_id = $4 AND
-                              account_id = $2 LIMIT 1),
-              dest_amount AS (SELECT amount FROM account_has_asset
-                               WHERE asset_id = $4 AND
-                               account_id = $3 LIMIT 1),
-              new_src_value AS (SELECT
-                              (SELECT
-                                  CASE WHEN EXISTS
-                                      (SELECT amount FROM src_amount LIMIT 1)
-                                      THEN
-                                      (SELECT amount FROM src_amount LIMIT 1)
-                                  ELSE 0::decimal
-                              END) - $6::decimal AS value
-                          ),
-              new_dest_value AS (SELECT
-                              (SELECT $6::decimal +
-                                  CASE WHEN EXISTS
-                                      (SELECT amount FROM dest_amount LIMIT 1)
-                                          THEN
-                                      (SELECT amount FROM dest_amount LIMIT 1)
-                                  ELSE 0::decimal
-                              END) AS value
-                          ),
+              new_src_quantity AS (
+                  SELECT coalesce(sum(amount), 0) - $6::decimal as value
+                  FROM account_has_asset
+                     WHERE asset_id = $4 AND
+                     account_id = $2
+              ),
+              new_dest_quantity AS (
+                  SELECT coalesce(sum(amount), 0) + $6::decimal as value
+                  FROM account_has_asset
+                     WHERE asset_id = $4 AND
+                     account_id = $3
+              ),
+              checks AS (
+                  -- error code and check result
+                  SELECT 3 code, count(1) = 1 result
+                  FROM account
+                  WHERE account_id = $2
+
+                  UNION
+                  SELECT 4, count(1) = 1
+                  FROM account
+                  WHERE account_id = $3
+
+                  UNION
+                  SELECT 5, count(1) = 1
+                  FROM asset
+                  WHERE asset_id = $4
+                     AND precision >= $5
+
+                  UNION
+                  SELECT 6, value >= 0
+                  FROM new_src_quantity
+
+                  UNION
+                  SELECT 7, value < (2::decimal ^ 256) / 10::decimal^$5
+                  FROM new_dest_quantity
+              ),
               insert_src AS
               (
-                  INSERT INTO account_has_asset(account_id, asset_id, amount)
-                  (
-                      SELECT $2, $4, value
-                      FROM new_src_value
-                      WHERE EXISTS (SELECT * FROM has_src_account LIMIT 1) AND
-                        EXISTS (SELECT * FROM has_dest_account LIMIT 1) AND
-                        EXISTS (SELECT * FROM has_asset LIMIT 1) AND
-                        EXISTS (SELECT value FROM new_src_value
-                                WHERE value >= 0 LIMIT 1) %s
-                  )
-                  ON CONFLICT (account_id, asset_id)
-                  DO UPDATE SET amount = EXCLUDED.amount
-                  RETURNING (1)
+                  UPDATE account_has_asset
+                  SET amount = value
+                  FROM new_src_quantity
+                  WHERE
+                      account_id = $2
+                      AND asset_id = $4
+                      AND (SELECT bool_and(checks.result) FROM checks) %s
               ),
               insert_dest AS
               (
                   INSERT INTO account_has_asset(account_id, asset_id, amount)
                   (
                       SELECT $3, $4, value
-                      FROM new_dest_value
-                      WHERE EXISTS (SELECT * FROM insert_src) AND
-                        EXISTS (SELECT * FROM has_src_account LIMIT 1) AND
-                        EXISTS (SELECT * FROM has_dest_account LIMIT 1) AND
-                        EXISTS (SELECT * FROM has_asset LIMIT 1) AND
-                        EXISTS (SELECT value FROM new_dest_value
-                                WHERE value < 2::decimal ^ (256 - $5)
-                                LIMIT 1) %s
+                      FROM new_dest_quantity
+                      WHERE (SELECT bool_and(checks.result) FROM checks) %s
                   )
                   ON CONFLICT (account_id, asset_id)
                   DO UPDATE SET amount = EXCLUDED.amount
                   RETURNING (1)
                )
           SELECT CASE
               WHEN EXISTS (SELECT * FROM insert_dest LIMIT 1) THEN 0
-              WHEN NOT EXISTS (SELECT * FROM has_dest_account LIMIT 1) THEN 4
-              WHEN NOT EXISTS (SELECT * FROM has_src_account LIMIT 1) THEN 3
-              WHEN NOT EXISTS (SELECT * FROM has_asset LIMIT 1) THEN 5
               %s
-              WHEN NOT EXISTS (SELECT value FROM new_src_value
-                               WHERE value >= 0 LIMIT 1) THEN 6
-              WHEN NOT EXISTS (SELECT value FROM new_dest_value
-                               WHERE value < 2::decimal ^ (256 - $5)
-                               LIMIT 1) THEN 7
-              ELSE 1
+              ELSE (SELECT code FROM checks WHERE not result LIMIT 1)
           END AS result)";
 
     const std::string PostgresCommandExecutor::compareAndSetAccountDetailBase =
```
