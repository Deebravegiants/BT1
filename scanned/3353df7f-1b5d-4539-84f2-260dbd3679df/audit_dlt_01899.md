# [?] fix: BWIP race condition (#2405)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-07-09
Source: https://github.com/matter-labs/zksync-era/commit/8099ab0b77da3168a4184611adecb98a7d32fbaa
Type: security-commit

## Details
fix: BWIP race condition (#2405)

## What ❔

Separately insert proof_generation_details and gen data blob URLs.

## Why ❔

Sometimes BWIP generates data before insert_proof_generation_details is
called, which results in errors.

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.

## Patch
### core/lib/dal/.sqlx/query-41a2731a3fe6ae441902632dcce15601ff39acd03e3c8a2265c9036b3dc54383.json
```diff
@@ -1,15 +0,0 @@
-{
-  "db_name": "PostgreSQL",
-  "query": "\n            INSERT INTO\n                proof_generation_details (l1_batch_number, status, proof_gen_data_blob_url, created_at, updated_at)\n            VALUES\n                ($1, 'unpicked', $2, NOW(), NOW())\n            ON CONFLICT (l1_batch_number) DO NOTHING\n            ",
-  "describe": {
-    "columns": [],
-    "parameters": {
-      "Left": [
-        "Int8",
-        "Text"
-      ]
-    },
-    "nullable": []
-  },
-  "hash": "41a2731a3fe6ae441902632dcce15601ff39acd03e3c8a2265c9036b3dc54383"
-}
```

### core/lib/dal/.sqlx/query-5137159db7d3ff456e368e6246b07554ce738a2d7005472e7e76a64a8fbd57ad.json
```diff
@@ -0,0 +1,14 @@
+{
+  "db_name": "PostgreSQL",
+  "query": "\n            INSERT INTO\n                proof_generation_details (l1_batch_number, status, created_at, updated_at)\n            VALUES\n                ($1, 'unpicked', NOW(), NOW())\n            ON CONFLICT (l1_batch_number) DO NOTHING\n            ",
+  "describe": {
+    "columns": [],
+    "parameters": {
+      "Left": [
+        "Int8"
+      ]
+    },
+    "nullable": []
+  },
+  "hash": "5137159db7d3ff456e368e6246b07554ce738a2d7005472e7e76a64a8fbd57ad"
+}
```

### core/lib/dal/.sqlx/query-b61b2545ff82bc3e2a198b21546735c1dcccdd6c439827fc4c3ba57e8767076e.json
```diff
@@ -0,0 +1,15 @@
+{
+  "db_name": "PostgreSQL",
+  "query": "\n            UPDATE proof_generation_details\n            SET\n                proof_gen_data_blob_url = $1,\n                updated_at = NOW()\n            WHERE\n                l1_batch_number = $2\n            ",
+  "describe": {
+    "columns": [],
+    "parameters": {
+      "Left": [
+        "Text",
+        "Int8"
+      ]
+    },
+    "nullable": []
+  },
+  "hash": "b61b2545ff82bc3e2a198b21546735c1dcccdd6c439827fc4c3ba57e8767076e"
+}
```

### core/lib/dal/migrations/20240708161016_remove-not-null-proof-gen-data-constraint.down.sql
```diff
@@ -0,0 +1 @@
+ALTER TABLE proof_generation_details ALTER COLUMN proof_gen_data_blob_url SET NOT NULL;
```

### core/lib/dal/migrations/20240708161016_remove-not-null-proof-gen-data-constraint.up.sql
```diff
@@ -0,0 +1 @@
+ALTER TABLE proof_generation_details ALTER COLUMN proof_gen_data_blob_url DROP NOT NULL;
```

### core/lib/dal/src/proof_generation_dal.rs
```diff
@@ -155,26 +155,60 @@ impl ProofGenerationDal<'_, '_> {
         Ok(())
     }
 
+    pub async fn save_merkle_paths_artifacts_metadata(
+        &mut self,
+        batch_number: L1BatchNumber,
+        proof_gen_data_blob_url: &str,
+    ) -> DalResult<()> {
+        let batch_number = i64::from(batch_number.0);
+        let query = sqlx::query!(
+            r#"
+            UPDATE proof_generation_details
+            SET
+                proof_gen_data_blob_url = $1,
+                updated_at = NOW()
+            WHERE
+                l1_batch_number = $2
+            "#,
+            proof_gen_data_blob_url,
+            batch_number
+        );
+        let instrumentation = Instrumented::new("save_proof_artifacts_metadata")
+            .with_arg("proof_gen_data_blob_url", &proof_gen_data_blob_url)
+            .with_arg("l1_batch_number", &batch_number);
+        let result = instrumentation
+            .clone()
+            .with(query)
+            .execute(self.storage)
+            .await?;
+        if result.rows_affected() == 0 {
+            let err = instrumentation.constraint_error(anyhow::anyhow!(
+                "Cannot save proof_gen_data_blob_url for a batch number {} that does not exist",
+                batch_number
+            ));
+            return Err(err);
+        }
+
+        Ok(())
+    }
+
     /// The caller should ensure that `l1_batch_number` exists in the database.
     pub async fn insert_proof_generation_details(
         &mut self,
         l1_batch_number: L1BatchNumber,
-        proof_gen_data_blob_url: &str,
     ) -> DalResult<()> {
         let result = sqlx::query!(
             r#"
             INSERT INTO
-                proof_generation_details (l1_batch_number, status, proof_gen_data_blob_url, created_at, updated_at)
+                proof_generation_details (l1_batch_number, status, created_at, updated_at)
             VALUES
-                ($1, 'unpicked', $2, NOW(), NOW())
+                ($1, 'unpicked', NOW(), NOW())
             ON CONFLICT (l1_batch_number) DO NOTHING
             "#,
-             i64::from(l1_batch_number.0),
-            proof_gen_data_blob_url,
+            i64::from(l1_batch_number.0),
         )
         .instrument("insert_proof_generation_details")
         .with_arg("l1_batch_number", &l1_batch_number)
-        .with_arg("proof_gen_data_blob_url", &proof_gen_data_blob_url)
         .report_latency()
         .execute(self.storage)
         .await?;
@@ -303,7 +337,7 @@ mod tests {
         assert_eq!(unpicked_l1_batch, None);
 
         conn.proof_generation_dal()
-            .insert_proof_generation_details(L1BatchNumber(1), "generation_data")
+            .insert_proof_generation_details(L1BatchNumber(1))
             .await
             .unwrap();
 
@@ -316,13 +350,17 @@ mod tests {
 
         // Calling the method multiple times should work fine.
         conn.proof_generation_dal()
-            .insert_proof_generation_details(L1BatchNumber(1), "generation_data")
+            .insert_proof_generation_details(L1BatchNumber(1))
             .await
             .unwrap();
         conn.proof_generation_dal()
             .save_vm_runner_artifacts_metadata(L1BatchNumber(1), "vm_run")
             .await
             .unwrap();
+        conn.proof_generation_dal()
+            .save_merkle_paths_artifacts_metadata(L1BatchNumber(1), "data")
+            .await
+            .unwrap();
         conn.blocks_dal()
             .save_l1_batch_tree_data(
                 L1BatchNumber(1),
```

### core/node/metadata_calculator/src/updater.rs
```diff
@@ -159,7 +159,11 @@ impl TreeUpdater {
                 // Save the proof generation details to Postgres
                 storage
                     .proof_generation_dal()
-                    .insert_proof_generation_details(l1_batch_number, object_key)
+                    .insert_proof_generation_details(l1_batch_number)
+                    .await?;
+                storage
+                    .proof_generation_dal()
+                    .save_merkle_paths_artifacts_metadata(l1_batch_number, object_key)
                     .await?;
             }
             drop(storage);
```

### core/node/vm_runner/src/impls/bwip.rs
```diff
@@ -172,6 +172,11 @@ impl StateKeeperOutputHandler for BasicWitnessInputProducerOutputHandler {
 
         tracing::info!(%l1_batch_number, "Saved VM run data");
 
+        connection
+            .proof_generation_dal()
+            .insert_proof_generation_details(l1_batch_number)
+            .await?;
+
         connection
             .proof_generation_dal()
             .save_vm_runner_artifacts_metadata(l1_batch_number, &blob_url)
```
