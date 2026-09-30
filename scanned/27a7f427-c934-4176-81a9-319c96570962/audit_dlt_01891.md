# [?] fix(tee): correct previous fix for race condition in batch locking (#3358)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-12-04
Source: https://github.com/matter-labs/zksync-era/commit/b12da8d1fddc7870bf17d5e08312d20773815269
Type: security-commit

## Details
fix(tee): correct previous fix for race condition in batch locking (#3358)

## What ❔

Commit a7dc0ed5007f6b2f789f4c61cb3d137843151860 (PR #3342) was supposed
to fix a race condition in batch locking by introducing SQL row-locking,
but it [didn't work][2] as expected.
![Screenshot From 2024-12-04
11-32-32](https://github.com/user-attachments/assets/959ffc3c-593f-409a-87ab-68ec197040a0)
Now we are switching back to coarser-grained table-level locking as
[originally suggested][1] by Harald. The original fix was hard to test
unless deployed to `stage` due to the undeterministic nature of the
problem, so we needed to merge it to the `main` branch to properly test
it.

[1]:
https://github.com/matter-labs/zksync-era/pull/3342#issuecomment-2514573386
[2]: https://grafana.matterlabs.dev/goto/AhEd5FVNg?orgId=1

## Why ❔

To fix the bug that only activates after running `zksync-tee-prover` on
multiple instances.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.

## Patch
### core/lib/dal/.sqlx/query-b6961d273f833f8babaf16f256822a6e92698fcfcf5d0a9252d84b75459b2664.json
```diff
@@ -1,6 +1,6 @@
 {
   "db_name": "PostgreSQL",
-  "query": "\n            SELECT\n                p.l1_batch_number\n            FROM\n                proof_generation_details p\n            LEFT JOIN\n                tee_proof_generation_details tee\n                ON\n                    p.l1_batch_number = tee.l1_batch_number\n                    AND tee.tee_type = $1\n            WHERE\n                (\n                    p.l1_batch_number >= $5\n                    AND p.vm_run_data_blob_url IS NOT NULL\n                    AND p.proof_gen_data_blob_url IS NOT NULL\n                )\n                AND (\n                    tee.l1_batch_number IS NULL\n                    OR (\n                        (tee.status = $2 OR tee.status = $3)\n                        AND tee.prover_taken_at < NOW() - $4::INTERVAL\n                    )\n                )\n            LIMIT 1\n            FOR UPDATE OF p\n            SKIP LOCKED\n            ",
+  "query": "\n            SELECT\n                p.l1_batch_number\n            FROM\n                proof_generation_details p\n            LEFT JOIN\n                tee_proof_generation_details tee\n                ON\n                    p.l1_batch_number = tee.l1_batch_number\n                    AND tee.tee_type = $1\n            WHERE\n                (\n                    p.l1_batch_number >= $5\n                    AND p.vm_run_data_blob_url IS NOT NULL\n                    AND p.proof_gen_data_blob_url IS NOT NULL\n                )\n                AND (\n                    tee.l1_batch_number IS NULL\n                    OR (\n                        (tee.status = $2 OR tee.status = $3)\n                        AND tee.prover_taken_at < NOW() - $4::INTERVAL\n                    )\n                )\n            LIMIT 1\n            ",
   "describe": {
     "columns": [
       {
@@ -22,5 +22,5 @@
       false
     ]
   },
-  "hash": "8ead57cdda5909348f31f8c4d989f73e353da3bc6af7ecb81102c4194df631aa"
+  "hash": "b6961d273f833f8babaf16f256822a6e92698fcfcf5d0a9252d84b75459b2664"
 }
```

### core/lib/dal/src/tee_proof_generation_dal.rs
```diff
@@ -66,10 +66,16 @@ impl TeeProofGenerationDal<'_, '_> {
         let min_batch_number = i64::from(min_batch_number.0);
         let mut transaction = self.storage.start_transaction().await?;
 
-        // Lock rows in the proof_generation_details table to prevent race conditions. The
-        // tee_proof_generation_details table does not have corresponding entries yet if this is the
-        // first time the query is invoked for a batch. Locking rows in proof_generation_details
-        // ensures that two different TEE prover instances will not try to prove the same batch.
+        // Lock the entire tee_proof_generation_details table in EXCLUSIVE mode to prevent race
+        // conditions. Locking the table ensures that two different TEE prover instances will not
+        // try to prove the same batch.
+        sqlx::query("LOCK TABLE tee_proof_generation_details IN EXCLUSIVE MODE")
+            .instrument("lock_batch_for_proving#lock_table")
+            .execute(&mut transaction)
+            .await?;
+
+        // The tee_proof_generation_details table does not have corresponding entries yet if this is
+        // the first time the query is invoked for a batch.
         let batch_number = sqlx::query!(
             r#"
             SELECT
@@ -95,8 +101,6 @@ impl TeeProofGenerationDal<'_, '_> {
                     )
                 )
             LIMIT 1
-            FOR UPDATE OF p
-            SKIP LOCKED
             "#,
             tee_type.to_string(),
             TeeProofGenerationJobStatus::PickedByProver.to_string(),
```
