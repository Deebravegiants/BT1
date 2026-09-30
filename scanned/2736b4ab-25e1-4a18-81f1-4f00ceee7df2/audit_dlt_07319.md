# [?] fix(icrc-rosetta): Fix timestamp overflow (#5249)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-05-22
Source: https://github.com/dfinity/ic/commit/fb478a889358a0fd2de594c6d13e4fd23e07a208
Type: security-commit

## Details
fix(icrc-rosetta): Fix timestamp overflow (#5249)

In Rosetta ICRC's `blocks` table, the timestamp fields `timestamp`,
`transaction_created_at_time` and `approval_expires_at` are defined with
`INTEGER` type, which is a *signed* 64-bit integer.

However, in the ledger's internal representation those are *unsigned*
64-bit integers, so when the value is over `i64::MAX`, it fails to store
it in the database. Since `approval_expires_at` is chosen by the user,
they can (and have) used such values, which makes the synchronization
fail entirely.

Although the other two fields are automatically defined, we're fixing
them too for the sake of consistency and fool-proofing.

This problem doesn't happen with ICP Rosetta because it stores
timestamps in `TEXT` fields, which we should replicate eventually in
ICRC1 Rosetta, although it's a much more disruptive change.

## Patch
### rs/rosetta-api/icrc1/BUILD.bazel
```diff
@@ -112,6 +112,14 @@ rust_test(
     deps = DEPENDENCIES + DEV_DEPENDENCIES,
 )
 
+rust_test(
+    name = "storage-operations-tests",
+    srcs = ["src/common/storage/storage_operations_test.rs"],
+    aliases = ALIASES,
+    proc_macro_deps = MACRO_DEPENDENCIES,
+    deps = DEPENDENCIES + [":ic-icrc-rosetta"],
+)
+
 LOCAL_REPLICA_DATA = [
     "//rs/canister_sandbox",
     "//rs/canister_sandbox:sandbox_launcher",
```

### rs/rosetta-api/icrc1/src/common/storage/storage_operations.rs
```diff
@@ -320,14 +320,25 @@ pub fn store_blocks(
                 expires_at,
             ),
         };
+
+        // SQLite doesn't support unsigned 64-bit integers. We need to convert the timestamps to signed
+        // 64-bit integers before storing them.
+        // TODO: Change the timestamps to a text type. Keeping timestamps as signed integers can cause
+        // issues if someone tries to compare them directly in the DB.
+        let timestamp = rosetta_block.get_timestamp();
+        let timestamp_i64 = convert_timestamp_to_db(timestamp);
+        let transaction_created_at_time_i64 =
+            transaction.created_at_time.map(convert_timestamp_to_db);
+        let approval_expires_at_i64 = approval_expires_at.map(convert_timestamp_to_db);
+
         insert_tx.prepare_cached(
         "INSERT OR IGNORE INTO blocks (idx, hash, serialized_block, parent_hash, timestamp,tx_hash,operation_type,from_principal,from_subaccount,to_principal,to_subaccount,spender_principal,spender_subaccount,memo,amount,expected_allowance,fee,transaction_created_at_time,approval_expires_at) VALUES (:idx, :hash, :serialized_block, :parent_hash, :timestamp,:tx_hash,:operation_type,:from_principal,:from_subaccount,:to_principal,:to_subaccount,:spender_principal,:spender_subaccount,:memo,:amount,:expected_allowance,:fee,:transaction_created_at_time,:approval_expires_at)")?
                     .execute(named_params! {
                         ":idx":rosetta_block.index,
                         ":hash":rosetta_block.clone().get_block_hash().as_slice().to_vec(),
                         ":serialized_block":rosetta_block.block,
                         ":parent_hash":rosetta_block.get_parent_hash().clone().map(|hash| hash.as_slice().to_vec()),
-                        ":timestamp":rosetta_block.get_timestamp(),
+                        ":timestamp":timestamp_i64,
                         ":tx_hash":rosetta_block.clone().get_transaction_hash().as_slice().to_vec(),
                         ":operation_type":operation_type,
                         ":from_principal":from_principal.map(|x| x.as_slice().to_vec()),
@@ -340,14 +351,27 @@ pub fn store_blocks(
                         ":amount":amount.to_string(),
                         ":expected_allowance":expected_allowance.map(|ea| ea.to_string()),
                         ":fee":fee.map(|fee| fee.to_string()),
-                        ":transaction_created_at_time":transaction.created_at_time,
-                        ":approval_expires_at":approval_expires_at
+                        ":transaction_created_at_time":transaction_created_at_time_i64,
+                        ":approval_expires_at":approval_expires_at_i64
                     })?;
     }
     insert_tx.commit()?;
     Ok(())
 }
 
+// Helper function to convert u64 timestamp to i64 for database storage
+fn convert_timestamp_to_db(timestamp: u64) -> i64 {
+    // Check if timestamp exceeds i64::MAX
+    if timestamp > i64::MAX as u64 {
+        // For values exceeding i64::MAX, we need to preserve the lower bits
+        // but represent them as a negative number in two's complement
+        ((timestamp & 0x7fffffffffffffff) as i64) | i64::MIN
+    } else {
+        // Safe conversion when within i64 range
+        timestamp as i64
+    }
+}
+
 // Returns a RosettaBlock if the block index exists in the database, else returns None.
 // Returns an Error if the query fails.
 pub fn get_block_at_idx(
```

### rs/rosetta-api/icrc1/src/common/storage/storage_operations_test.rs
```diff
@@ -0,0 +1,392 @@
+use candid::{Nat, Principal};
+use ic_icrc_rosetta::common::storage::storage_operations::*;
+use ic_icrc_rosetta::common::storage::types::{
+    IcrcBlock, IcrcOperation, IcrcTransaction, RosettaBlock,
+};
+use icrc_ledger_types::icrc1::account::Account;
+use rusqlite::{params, Connection};
+use tempfile::tempdir;
+
+// Helper function to create a test block with a specific timestamp and data
+fn create_test_rosetta_block(
+    index: u64,
+    timestamp: u64,
+    principal: &[u8],
+    amount: u64,
+) -> RosettaBlock {
+    // Create owner account
+    let owner = Account {
+        owner: Principal::from_slice(principal),
+        subaccount: None,
+    };
+
+    // Create recipient account (just use a different principal)
+    let mut recipient_principal = principal.to_vec();
+    if !recipient_principal.is_empty() {
+        recipient_principal[0] = recipient_principal[0].wrapping_add(1);
+    }
+    let recipient = Account {
+        owner: Principal::from_slice(&recipient_principal),
+        subaccount: None,
+    };
+
+    // Create a transfer transaction
+    let transaction = IcrcTransaction {
+        operation: IcrcOperation::Transfer {
+            from: owner,
+            to: recipient,
+            amount: Nat::from(amount),
+            fee: Some(Nat::from(1u64)),
+            spender: None,
+        },
+        memo: None,
+        created_at_time: Some(timestamp),
+    };
+
+    // Create a block with the transaction
+    let icrc_block = IcrcBlock {
+        parent_hash: None,
+        transaction,
+        timestamp,
+        effective_fee: None,
+        fee_collector: None,
+        fee_collector_block_index: None,
+    };
+
+    RosettaBlock {
+        index,
+        block: icrc_block,
+    }
+}
+
+// Helper function to create a test block with an approve operation and specified timestamps
+fn create_test_approve_block(
+    index: u64,
+    block_timestamp: u64,
+    created_at_time: u64,
+    expires_at: u64,
+    principal: &[u8],
+) -> RosettaBlock {
+    // Create owner account
+    let owner = Account {
+        owner: Principal::from_slice(principal),
+        subaccount: None,
+    };
+
+    // Create spender account (just use a different principal)
+    let mut spender_principal = principal.to_vec();
+    if !spender_principal.is_empty() {
+        spender_principal[0] = spender_principal[0].wrapping_add(1);
+    }
+    let spender = Account {
+        owner: Principal::from_slice(&spender_principal),
+        subaccount: None,
+    };
+
+    // Create an approve transaction
+    let transaction = IcrcTransaction {
+        operation: IcrcOperation::Approve {
+            from: owner,
+            spender,
+            amount: Nat::from(1000u64),
+            expected_allowance: None,
+            expires_at: Some(expires_at),
+            fee: Some(Nat::from(1u64)),
+        },
+        memo: None,
+        created_at_time: Some(created_at_time),
+    };
+
+    // Create a block with the transaction
+    let icrc_block = IcrcBlock {
+        parent_hash: None,
+        transaction,
+        timestamp: block_timestamp,
+        effective_fee: None,
+        fee_collector: None,
+        fee_collector_block_index: None,
+    };
+
+    RosettaBlock {
+        index,
+        block: icrc_block,
+    }
+}
+
+#[test]
+fn test_store_and_read_blocks() -> anyhow::Result<()> {
+    // Create a temporary directory and database
+    let temp_dir = tempdir()?;
+    let db_path = temp_dir.path().join("test_blocks_db.sqlite");
+
+    // Create and initialize database with necessary tables
+    let mut connection = Connection::open(&db_path)?;
+
+    // Create the blocks table (simplified version for the test)
+    connection.execute(
+        "CREATE TABLE blocks (
+            idx INTEGER PRIMARY KEY,
+            hash BLOB NOT NULL,
+            serialized_block BLOB NOT NULL,
+            parent_hash BLOB,
+            timestamp INTEGER,
+            tx_hash BLOB,
+            operation_type TEXT,
+            from_principal BLOB,
+            from_subaccount BLOB,
+            to_principal BLOB,
+            to_subaccount BLOB,
+            spender_principal BLOB,
+            spender_subaccount BLOB,
+            memo BLOB,
+            amount TEXT,
+            expected_allowance TEXT,
+            fee TEXT,
+            transaction_created_at_time INTEGER,
+            approval_expires_at INTEGER
+        )",
+        params![],
+    )?;
+
+    // Create test data
+    let principal1 = vec![1, 2, 3, 4];
+    let principal2 = vec![5, 6, 7, 8];
+
+    // Create timestamps of different sizes
+    let normal_timestamp = 1000000000u64;
+    let max_timestamp = i64::MAX as u64;
+    let beyond_max_timestamp = max_timestamp + 1;
+    let very_large_timestamp = u64::MAX;
+
+    // Create blocks with transfer operations and different block timestamps
+    let block0 = create_test_rosetta_block(0, normal_timestamp, &principal1, 100);
+    let block1 = create_test_rosetta_block(1, max_timestamp, &principal1, 200);
+    let block2 = create_test_rosetta_block(2, beyond_max_timestamp, &principal2, 300);
+    let block3 = create_test_rosetta_block(3, very_large_timestamp, &principal2, 400);
+
+    // Create a block with an approve operation that has approval_expires_at timestamp
+    let block4 = create_test_approve_block(
+        4,
+        normal_timestamp,     // block timestamp
+        beyond_max_timestamp, // created_at_time
+        very_large_timestamp, // expires_at
+        &principal1,
+    );
+
+    // Test storing blocks
+    store_blocks(
+        &mut connection,
+        vec![
+            block0.clone(),
+            block1.clone(),
+            block2.clone(),
+            block3.clone(),
+            block4.clone(),
+        ],
+    )?;
+
+    // Test get_block_at_idx
+    let retrieved_block0 = get_block_at_idx(&connection, 0)?.unwrap();
+    let retrieved_block1 = get_block_at_idx(&connection, 1)?.unwrap();
+    let retrieved_block2 = get_block_at_idx(&connection, 2)?.unwrap();
+    let retrieved_block3 = get_block_at_idx(&connection, 3)?.unwrap();
+    let retrieved_block4 = get_block_at_idx(&connection, 4)?.unwrap();
+
+    // Verify all blocks were retrieved correctly - block timestamps
+    assert_eq!(retrieved_block0.index, block0.index);
+    assert_eq!(retrieved_block0.get_timestamp(), normal_timestamp);
+
+    assert_eq!(retrieved_block1.index, block1.index);
+    assert_eq!(retrieved_block1.get_timestamp(), max_timestamp);
+
+    assert_eq!(retrieved_block2.index, block2.index);
+    assert_eq!(retrieved_block2.get_timestamp(), beyond_max_timestamp);
+
+    assert_eq!(retrieved_block3.index, block3.index);
+    assert_eq!(retrieved_block3.get_timestamp(), very_large_timestamp);
+
+    // Verify transaction_created_at_time is preserved for all blocks
+    assert_eq!(
+        retrieved_block0.block.transaction.created_at_time,
+        block0.block.transaction.created_at_time
+    );
+
+    assert_eq!(
+        retrieved_block2.block.transaction.created_at_time,
+        block2.block.transaction.created_at_time
+    );
+
+    assert_eq!(
+        retrieved_block3.block.transaction.created_at_time,
+        block3.block.transaction.created_at_time
+    );
+
+    // Verify approve operation specific fields on block4
+    match &retrieved_block4.block.transaction.operation {
+        IcrcOperation::Approve { expires_at, .. } => {
+            // Verify approval_expires_at timestamp is preserved
+            assert_eq!(
+                *expires_at,
+                Some(very_large_timestamp),
+                "approval_expires_at timestamp not preserved correctly"
+            );
+        }
+        _ => panic!("Expected Approve operation for block4"),
+    }
+
+    // Verify created_at_time is preserved for the approve block
+    assert_eq!(
+        retrieved_block4.block.transaction.created_at_time,
+        Some(beyond_max_timestamp),
+        "transaction_created_at_time not preserved correctly for approve block"
+    );
+
+    Ok(())
+}
+
+#[test]
+fn test_hash_consistency() -> anyhow::Result<()> {
+    // Create a temporary directory and database
+    let temp_dir = tempdir()?;
+    let db_path = temp_dir.path().join("test_hash_db.sqlite");
+
+    // Initialize database with necessary tables
+    let mut connection = Connection::open(&db_path)?;
+
+    connection.execute(
+        "CREATE TABLE blocks (
+            idx INTEGER PRIMARY KEY,
+            hash BLOB NOT NULL,
+            serialized_block BLOB NOT NULL,
+            parent_hash BLOB,
+            timestamp INTEGER,
+            tx_hash BLOB,
+            operation_type TEXT,
+            from_principal BLOB,
+            from_subaccount BLOB,
+            to_principal BLOB,
+            to_subaccount BLOB,
+            spender_principal BLOB,
+            spender_subaccount BLOB,
+            memo BLOB,
+            amount TEXT,
+            expected_allowance TEXT,
+            fee TEXT,
+            transaction_created_at_time INTEGER,
+            approval_expires_at INTEGER
+        )",
+        params![],
+    )?;
+
+    // Create test data - blocks with different timestamp values and operations
+    let principal1 = vec![1, 2, 3, 4];
+    let principal2 = vec![5, 6, 7, 8];
+
+    // Create blocks with different timestamps and operations
+    let normal_timestamp = 1000000000u64;
+    let max_timestamp = i64::MAX as u64;
+    let beyond_max_timestamp = max_timestamp + 1;
+
+    // Create blocks for testing
+    let blocks = vec![
+        create_test_rosetta_block(0, normal_timestamp, &principal1, 100),
+        create_test_rosetta_block(1, max_timestamp, &principal1, 200),
+        create_test_rosetta_block(2, beyond_max_timestamp, &principal2, 300),
+        create_test_approve_block(
+            3,
+            normal_timestamp,
+            beyond_max_timestamp,
+            max_timestamp,
+            &principal1,
+        ),
+    ];
+
+    // Record original hashes for comparison
+    let original_block_hashes: Vec<_> = blocks
+        .iter()
+        .map(|block| block.clone().get_block_hash())
+        .collect();
+
+    let original_tx_hashes: Vec<_> = blocks
+        .iter()
+        .map(|block| block.clone().get_transaction_hash())
+        .collect();
+
+    // Store blocks in the database
+    store_blocks(&mut connection, blocks.clone())?;
+
+    // Retrieve blocks from the database
+    let retrieved_blocks: Vec<_> = (0..blocks.len())
+        .map(|idx| get_block_at_idx(&connection, idx as u64).unwrap().unwrap())
+        .collect();
+
+    // Verify block hashes match the original values
+    for (i, block) in retrieved_blocks.iter().enumerate() {
+        assert_eq!(
+            block.clone().get_block_hash(),
+            original_block_hashes[i],
+            "Block hash mismatch for block index {}",
+            i
+        );
+
+        assert_eq!(
+            block.clone().get_transaction_hash(),
+            original_tx_hashes[i],
+            "Transaction hash mismatch for block index {}",
+            i
+        );
+    }
+
+    // Test retrieving blocks by hash
+    for (i, original_hash) in original_block_hashes.iter().enumerate() {
+        let block_by_hash = get_block_by_hash(&connection, original_hash.clone())?
+            .unwrap_or_else(|| panic!("Block with hash {:?} not found", original_hash));
+
+        assert_eq!(
+            block_by_hash.index, i as u64,
+            "Retrieved wrong block by hash for index {}",
+            i
+        );
+
+        assert_eq!(
+            block_by_hash.clone().get_block_hash(),
+            original_block_hashes[i],
+            "Block hash doesn't match for block retrieved by hash, index {}",
+            i
+        );
+    }
+
+    // Test retrieving blocks by transaction hash
+    for (i, original_tx_hash) in original_tx_hashes.iter().enumerate() {
+        let blocks_by_tx = get_blocks_by_transaction_hash(&connection, original_tx_hash.clone())?;
+
+        assert_eq!(
+            blocks_by_tx.len(),
+            1,
+            "Expected exactly one block with transaction hash {:?}",
+            original_tx_hash
+        );
+
+        assert_eq!(
+            blocks_by_tx[0].index, i as u64,
+            "Retrieved wrong block by transaction hash for index {}",
+            i
+        );
+
+        assert_eq!(
+            blocks_by_tx[0].clone().get_block_hash(),
+            original_block_hashes[i],
+            "Block hash doesn't match for block retrieved by transaction hash, index {}",
+            i
+        );
+
+        assert_eq!(
+            blocks_by_tx[0].clone().get_transaction_hash(),
+            original_tx_hashes[i],
+            "Transaction hash doesn't match for block retrieved by transaction hash, index {}",
+            i
+        );
+    }
+
+    Ok(())
+}
```
