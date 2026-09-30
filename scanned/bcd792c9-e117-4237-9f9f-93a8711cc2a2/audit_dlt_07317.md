# [?] fix(icp-rosetta): fix integer overflow for balances (#5401)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-06-13
Source: https://github.com/dfinity/ic/commit/d96a92228fb7e6c13ea2d51f91250db240189425
Type: security-commit

## Details
fix(icp-rosetta): fix integer overflow for balances (#5401)

Balances are being stored as signed int64 in ICP Rosetta's SQLite
database. Balances, however, can go beyond INT64_MAX as they are
ultimately unsigned 64-bit integers.

We recently funded an account with more than INT64_MAX test tokens
(TESTICP), which made ICP Rosetta fail to synchronize blocks when
pointing at the TESTICP ledger:

 ```
2025-06-03T12:25:38.221738Z ERROR
rs/rosetta-api/icp/src/rosetta_server.rs:454: Error in syncing blocks:
InternalError(false, Details { error_message: Some("out of range
integral type conversion attempted | Block IDX: 3008 , Account
02dfb592f51fce16a7969f2aaf3279767679e14d2869b5819e902b3674384740, Tokens
10000000000000000000"), extra_fields: {} })
 ```
 
This PR makes rosetta store balances higher than INT64_MAX as negative
numbers (2-complement), solving the problem in a backwards compatible
way.

Tracked in [FI-1738](https://dfinity.atlassian.net/browse/FI-1738).

[FI-1738]:
https://dfinity.atlassian.net/browse/FI-1738?atlOrigin=eyJpIjoiNWRkNTljNzYxNjVmNDY3MDlhMDU5Y2ZhYzA5YTRkZjUiLCJwIjoiZ2l0aHViLWNvbS1KU1cifQ

## Patch
### rs/rosetta-api/icp/ledger_canister_blocks_synchronizer/src/blocks.rs
```diff
@@ -349,12 +349,15 @@ mod database_access {
             .unwrap();
         let amount = stmt
             .query_map(params![block_idx, account.to_hex()], |row| {
-                Ok(row.get(0).unwrap())
+                // Read as i64 and reinterpret as u64 to handle the full u64 range
+                let tokens_i64: i64 = row.get(0)?;
+                let tokens_u64 = tokens_i64 as u64;
+                Ok(tokens_u64)
             })
             .unwrap()
             .next();
         match amount {
-            Some(tokens) => Ok(tokens.unwrap()),
+            Some(tokens) => Ok(Some(tokens.unwrap())),
             None => Ok(None),
         }
     }
@@ -370,7 +373,11 @@ mod database_access {
             |account: AccountIdentifier| -> Result<Option<(String, u64)>, BlockStoreError> {
                 let account_balance_opt = stmt_select
                     .query_map(params![account.to_hex(), hb.index], |row| {
-                        Ok((row.get(1).map(|x: String| x as String)?, row.get(2)?))
+                        let account: String = row.get(1)?;
+                        // Read as i64 and reinterpret as u64 to handle the full u64 range
+                        let tokens_i64: i64 = row.get(2)?;
+                        let tokens_u64 = tokens_i64 as u64;
+                        Ok((account, tokens_u64))
                     })
                     .map_err(|e| BlockStoreError::Other(e.to_string()))?
                     .map(|x| x.unwrap())
@@ -472,8 +479,10 @@ mod database_access {
         }
 
         for (account, tokens) in new_balances {
+            // Store u64 as i64 using bit-reinterpretation to handle the full u64 range
+            let tokens_i64 = tokens as i64;
             stmt_insert
-                .execute(params![hb.index, account, tokens])
+                .execute(params![hb.index, account, tokens_i64])
                 .map_err(|e| {
                     BlockStoreError::Other(
                         e.to_string()
@@ -592,7 +601,11 @@ mod database_access {
             .unwrap();
         let account_history = stmt
             .query_map(params![account], |row| {
-                Ok((row.get(0)?, row.get(1).map(Tokens::from_e8s)?))
+                let block_idx: u64 = row.get(0)?;
+                // Read as i64 and reinterpret as u64 to handle the full u64 range
+                let tokens_i64: i64 = row.get(1)?;
+                let tokens_u64 = tokens_i64 as u64;
+                Ok((block_idx, Tokens::from_e8s(tokens_u64)))
             })
             .map_err(|e| BlockStoreError::Other(e.to_string()))?;
         for tuple in account_history {
@@ -1709,4 +1722,177 @@ VALUES (:idx, :block_idx)"#,
         let actual_rosetta_block = blocks.get_rosetta_block(0).unwrap();
         assert_eq!(rosetta_block, actual_rosetta_block);
     }
+
+    #[test]
+    fn test_update_balance_book_with_large_values() {
+        let mut blocks = Blocks::new_in_memory(false).unwrap();
+
+        let account = AccountIdentifier::new(ic_types::PrincipalId(Principal::anonymous()), None);
+
+        // Create a mint transaction with a large amount
+        let large_amount = 10000000000000000000u64; // Exceeds i64::MAX
+        let transaction = Transaction {
+            operation: Operation::Mint {
+                to: account,
+                amount: Tokens::from_e8s(large_amount),
+            },
+            memo: Memo(0),
+            created_at_time: None,
+            icrc1_memo: None,
+        };
+
+        let block = Block {
+            parent_hash: None,
+            transaction,
+            timestamp: TimeStamp::from_nanos_since_unix_epoch(1),
+        };
+
+        let encoded_block = block.clone().encode();
+        let hashed_block = super::HashedBlock::hash_block(encoded_block, None, 0, block.timestamp);
+
+        // Push the block (this should handle the large value correctly with TEXT storage)
+        blocks.push(&hashed_block).unwrap();
+
+        // Set the block as verified so we can query the balance
+        blocks.set_hashed_block_to_verified(&0).unwrap();
+
+        // Verify the balance was stored and can be retrieved with full precision
+        let balance = blocks.get_account_balance(&account, &0).unwrap();
+        assert_eq!(balance, Tokens::from_e8s(large_amount));
+
+        // Verify the balance history
+        let history = blocks.get_account_balance_history(&account, None).unwrap();
+        assert_eq!(history.len(), 1);
+        assert_eq!(history[0], (0u64, Tokens::from_e8s(large_amount)));
+    }
+
+    #[test]
+    fn test_comprehensive_backwards_compatibility() {
+        use super::database_access;
+        use rusqlite::params;
+
+        let blocks = Blocks::new_in_memory(false).unwrap();
+        let mut connection = blocks.connection.lock().unwrap();
+
+        let account1 = AccountIdentifier::new(ic_types::PrincipalId(Principal::anonymous()), None);
+        let account2 = AccountIdentifier::new(
+            ic_types::PrincipalId(Principal::from_slice(&[1u8; 29])),
+            None,
+        );
+
+        // Scenario 1: Existing database with small INTEGER values (backwards compatible)
+        let small_value1 = 1000000u64; // 0.01 ICP
+        let small_value2 = 5000000000u64; // 50 ICP
+        connection
+            .execute(
+                "INSERT INTO account_balances (block_idx, account, tokens) VALUES (?1, ?2, ?3)",
+                params![1u64, account1.to_hex(), small_value1 as i64],
+            )
+            .unwrap();
+        connection
+            .execute(
+                "INSERT INTO account_balances (block_idx, account, tokens) VALUES (?1, ?2, ?3)",
+                params![2u64, account2.to_hex(), small_value2 as i64],
+            )
+            .unwrap();
+
+        // Scenario 2: New large values using bit-reinterpretation
+        let large_value1 = 10000000000000000000u64; // The problematic value from the original error
+        let large_value2 = 18446744073709551615u64; // u64::MAX
+        connection
+            .execute(
+                "INSERT INTO account_balances (block_idx, account, tokens) VALUES (?1, ?2, ?3)",
+                params![3u64, account1.to_hex(), large_value1 as i64], // Stored as negative i64
+            )
+            .unwrap();
+        connection
+            .execute(
+                "INSERT INTO account_balances (block_idx, account, tokens) VALUES (?1, ?2, ?3)",
+                params![4u64, account2.to_hex(), large_value2 as i64], // Stored as -1
+            )
+            .unwrap();
+
+        // Test reading all values - should work seamlessly with bit-reinterpretation
+        let balance1 =
+            database_access::get_account_balance(&mut connection, &1u64, &account1).unwrap();
+        let balance2 =
+            database_access::get_account_balance(&mut connection, &2u64, &account2).unwrap();
+        let balance3 =
+            database_access::get_account_balance(&mut connection, &3u64, &account1).unwrap();
+        let balance4 =
+            database_access::get_account_balance(&mut connection, &4u64, &account2).unwrap();
+
+        // All values should be read correctly regardless of magnitude
+        assert_eq!(balance1, Some(small_value1));
+        assert_eq!(balance2, Some(small_value2));
+        assert_eq!(balance3, Some(large_value1));
+        assert_eq!(balance4, Some(large_value2));
+
+        // Test that the latest balance query works correctly (should return the large values)
+        let latest_balance1 =
+            database_access::get_account_balance(&mut connection, &10u64, &account1).unwrap();
+        let latest_balance2 =
+            database_access::get_account_balance(&mut connection, &10u64, &account2).unwrap();
+
+        assert_eq!(latest_balance1, Some(large_value1));
+        assert_eq!(latest_balance2, Some(large_value2));
+    }
+
+    #[test]
+    fn test_account_balance_bit_reinterpretation() {
+        use super::database_access;
+        use rusqlite::params;
+
+        let blocks = Blocks::new_in_memory(false).unwrap();
+        let mut connection = blocks.connection.lock().unwrap();
+
+        let account = AccountIdentifier::new(ic_types::PrincipalId(Principal::anonymous()), None);
+
+        // Test 1: Small value (fits in i64) - stored as positive
+        let small_value = 1000000u64; // 0.01 ICP in e8s
+        connection
+            .execute(
+                "INSERT INTO account_balances (block_idx, account, tokens) VALUES (?1, ?2, ?3)",
+                params![1u64, account.to_hex(), small_value as i64],
+            )
+            .unwrap();
+
+        let balance =
+            database_access::get_account_balance(&mut connection, &1u64, &account).unwrap();
+        assert_eq!(balance, Some(small_value));
+
+        // Test 2: Large value (exceeds i64::MAX) - stored as negative i64, reinterpreted as u64
+        let large_value = 10000000000000000000u64; // Exceeds i64::MAX
+        let large_value_as_i64 = large_value as i64; // This becomes negative
+        connection
+            .execute(
+                "INSERT INTO account_balances (block_idx, account, tokens) VALUES (?1, ?2, ?3)",
+                params![2u64, account.to_hex(), large_value_as_i64],
+            )
+            .unwrap();
+
+        let balance =
+            database_access::get_account_balance(&mut connection, &2u64, &account).unwrap();
+        assert_eq!(balance, Some(large_value)); // Should recover the original value
+
+        // Test 3: u64::MAX value
+        let max_value = u64::MAX;
+        let max_value_as_i64 = max_value as i64; // This becomes -1
+        connection
+            .execute(
+                "INSERT INTO account_balances (block_idx, account, tokens) VALUES (?1, ?2, ?3)",
+                params![3u64, account.to_hex(), max_value_as_i64],
+            )
+            .unwrap();
+
+        let balance =
+            database_access::get_account_balance(&mut connection, &3u64, &account).unwrap();
+        assert_eq!(balance, Some(max_value)); // Should recover u64::MAX
+
+        // Verify that bit reinterpretation works correctly
+        assert_eq!(large_value_as_i64, -8446744073709551616i64);
+        assert_eq!(max_value_as_i64, -1i64);
+        assert_eq!((-8446744073709551616i64) as u64, 10000000000000000000u64);
+        assert_eq!((-1i64) as u64, u64::MAX);
+    }
 }
```
