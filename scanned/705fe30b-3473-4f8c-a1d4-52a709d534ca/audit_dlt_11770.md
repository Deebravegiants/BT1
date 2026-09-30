# [?] Add test for double-spend protection

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-12-04
Source: https://github.com/AleoNet/snarkVM-test/commit/dc0761a3562ff5642731f7b7047dbba47052e4e2
Type: security-commit

## Details
Add test for double-spend protection

## Patch
### ledger/src/tests.rs
```diff
@@ -636,3 +636,83 @@ fn test_aborted_transaction_indexing() {
     // Add the deployment block to the ledger.
     ledger.advance_to_next_block(&block).unwrap();
 }
+
+#[test]
+fn test_execute_duplicate_input_ids() {
+    let rng = &mut TestRng::default();
+
+    // Initialize the test environment.
+    let crate::test_helpers::TestEnv { ledger, private_key, view_key, address, .. } =
+        crate::test_helpers::sample_test_env(rng);
+
+    // A helper function to find records.
+    let find_records = || {
+        let microcredits = Identifier::from_str("microcredits").unwrap();
+        ledger
+            .find_records(&view_key, RecordsFilter::SlowUnspent(private_key))
+            .unwrap()
+            .filter(|(_, record)| match record.data().get(&microcredits) {
+                Some(Entry::Private(Plaintext::Literal(Literal::U64(amount), _))) => !amount.is_zero(),
+                _ => false,
+            })
+            .collect::<indexmap::IndexMap<_, _>>()
+    };
+
+    // Fetch the unspent records.
+    let records = find_records();
+    let record_1 = records[0].clone();
+
+    // Prepare a transfer that spends the record.
+    let inputs = [
+        Value::Record(record_1.clone()),
+        Value::from_str(&format!("{address}")).unwrap(),
+        Value::from_str("100u64").unwrap(),
+    ];
+    let transfer_1 = ledger
+        .vm
+        .execute(&private_key, ("credits.aleo", "transfer_private"), inputs.into_iter(), None, 0, None, rng)
+        .unwrap();
+    let transfer_1_id = transfer_1.id();
+
+    // Prepare a transfer that attempts to spend the same record.
+    let inputs = [
+        Value::Record(record_1.clone()),
+        Value::from_str(&format!("{address}")).unwrap(),
+        Value::from_str("1000u64").unwrap(),
+    ];
+    let transfer_2 = ledger
+        .vm
+        .execute(&private_key, ("credits.aleo", "transfer_private"), inputs.into_iter(), None, 0, None, rng)
+        .unwrap();
+    let transfer_2_id = transfer_2.id();
+
+    // Prepare a transfer that attempts to spend the same record in the fee.
+    let inputs = [Value::from_str(&format!("{address}")).unwrap(), Value::from_str("100u64").unwrap()];
+    let transfer_3 = ledger
+        .vm
+        .execute(&private_key, ("credits.aleo", "transfer_public"), inputs.into_iter(), Some(record_1), 0, None, rng)
+        .unwrap();
+    let transfer_3_id = transfer_3.id();
+
+    // Create a block.
+    let block = ledger
+        .prepare_advance_to_next_beacon_block(
+            &private_key,
+            vec![],
+            vec![],
+            vec![transfer_1, transfer_2, transfer_3],
+            rng,
+        )
+        .unwrap();
+
+    // Check that the next block is valid.
+    ledger.check_next_block(&block, rng).unwrap();
+
+    // Add the block to the ledger.
+    ledger.advance_to_next_block(&block).unwrap();
+
+    // Enforce that the block transactions were correct.
+    assert_eq!(block.transactions().num_accepted(), 1);
+    assert_eq!(block.transactions().transaction_ids().collect::<Vec<_>>(), vec![&transfer_1_id]);
+    assert_eq!(block.aborted_transaction_ids(), &vec![transfer_2_id, transfer_3_id]);
+}
```
