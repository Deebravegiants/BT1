# [?] store: split dump batches by byte size to avoid 2GB Arrow column overflow (#6646)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2026-06-26
Source: https://github.com/graphprotocol/graph-node/commit/9a441c74d9252502f5581b2bcc682468d5e5313b
Type: security-commit

## Details
store: split dump batches by byte size to avoid 2GB Arrow column overflow (#6646)

## Patch
### store/postgres/src/parquet/convert.rs
```diff
@@ -58,6 +58,39 @@ pub fn rows_to_record_batch(schema: &Schema, rows: &[OidRow]) -> Result<RecordBa
         .map_err(|e| StoreError::InternalError(format!("failed to build RecordBatch: {e}")))
 }
 
+/// Conservative estimate of the number of payload bytes a row contributes to an
+/// Arrow `RecordBatch`. The dumper uses this to bound batch size so that no
+/// single 32-bit-offset string/binary column can exceed Arrow's 2 GiB offset
+/// limit while a large table is dumped (issue #6609). Variable-length payloads
+/// (`String`/`Bytes`) dominate that limit and are counted exactly; fixed-width
+/// values use their in-memory width.
+pub(crate) fn estimate_row_bytes(row: &OidRow) -> usize {
+    row.into_iter().map(estimate_value_bytes).sum()
+}
+
+fn estimate_value_bytes(value: &OidValue) -> usize {
+    match value {
+        OidValue::Null => 0,
+        OidValue::Bool(_) => 1,
+        OidValue::Int(_) => 4,
+        OidValue::Int8(_) => 8,
+        OidValue::Timestamp(_) => 8,
+        OidValue::Int4Range(_, _) => 8,
+        OidValue::Bytes(v) => v.as_ref().len(),
+        OidValue::String(v) => v.len(),
+        // Decimals are dumped as their decimal-string representation; 64 bytes
+        // is a comfortable upper bound for realistic values.
+        OidValue::BigDecimal(_) => 64,
+        OidValue::BoolArray(v) => v.len(),
+        OidValue::Ints(v) => v.len() * 4,
+        OidValue::Int8Array(v) => v.len() * 8,
+        OidValue::TimestampArray(v) => v.len() * 8,
+        OidValue::BytesArray(v) => v.iter().map(|b| b.as_ref().len()).sum(),
+        OidValue::StringArray(v) => v.iter().map(|s| s.len()).sum(),
+        OidValue::BigDecimalArray(v) => v.len() * 64,
+    }
+}
+
 /// A type-erased column builder that wraps the appropriate Arrow array builder.
 enum ColumnBuilder {
     Boolean(BooleanBuilder),
```

### store/postgres/src/relational/dump.rs
```diff
@@ -19,7 +19,7 @@ use serde::{Deserialize, Serialize};
 use crate::AsyncPgConnection;
 use crate::catalog;
 use crate::detail::deployment_entity;
-use crate::parquet::convert::rows_to_record_batch;
+use crate::parquet::convert::{estimate_row_bytes, rows_to_record_batch};
 use crate::parquet::schema::{arrow_schema, clamp_arrow_schema, data_sources_arrow_schema};
 use crate::parquet::writer::{ChunkInfo, ParquetChunkWriter};
 use crate::relational::dsl;
@@ -262,6 +262,37 @@ fn chunk_filename(index: usize) -> String {
     format!("chunk_{:06}.parquet", index)
 }
 
+/// Maximum estimated payload size of a single Arrow `RecordBatch`. Kept well
+/// under Arrow's 2 GiB i32 offset limit so that no single string/binary column
+/// can overflow while a large table is dumped. The adaptive `VidBatcher` sizes
+/// fetches by elapsed time with no byte ceiling, so a single fetch can hold far
+/// more than this; we therefore split each fetched batch into byte-bounded
+/// `RecordBatch`es before writing (issue #6609).
+const MAX_RECORD_BATCH_BYTES: usize = 256 * 1024 * 1024;
+
+/// Split `rows` (ordered by vid) into contiguous sub-slices whose estimated
+/// payload size each stays at or below `max_bytes`. Always emits at least one
+/// row per slice, so an oversized single row still makes progress (a lone row
+/// can never overflow a column, since Postgres caps any field at ~1 GiB).
+fn byte_bounded_slices(rows: &[OidRow], max_bytes: usize) -> Vec<&[OidRow]> {
+    let mut slices = Vec::new();
+    let mut start = 0;
+    let mut acc = 0usize;
+    for (i, row) in rows.iter().enumerate() {
+        let sz = estimate_row_bytes(row);
+        if i > start && acc + sz > max_bytes {
+            slices.push(&rows[start..i]);
+            start = i;
+            acc = 0;
+        }
+        acc += sz;
+    }
+    if start < rows.len() {
+        slices.push(&rows[start..]);
+    }
+    slices
+}
+
 fn clamp_filename(index: usize) -> String {
     format!("clamp_{:06}.parquet", index)
 }
@@ -708,10 +739,13 @@ async fn dump_entity_table(
                 }
 
                 let count = rows.len();
-                let batch = rows_to_record_batch(&arrow_schema, &rows)?;
-                let batch_min_vid = start;
-                let batch_max_vid = end;
-                writer.write_batch(&batch, batch_min_vid, batch_max_vid)?;
+                // A single adaptive fetch can hold far more than Arrow's 2 GiB
+                // per-column offset limit allows; split it into byte-bounded
+                // `RecordBatch`es so no string/binary column can overflow (#6609).
+                for sub in byte_bounded_slices(&rows, MAX_RECORD_BATCH_BYTES) {
+                    let batch = rows_to_record_batch(&arrow_schema, sub)?;
+                    writer.write_batch(&batch, start, end)?;
+                }
                 Ok(count)
             })
             .await?;
@@ -1201,6 +1235,36 @@ mod tests {
         assert_eq!(clamp_filename(1), "clamp_000001.parquet");
     }
 
+    #[test]
+    fn byte_bounded_slices_split_and_preserve_rows() {
+        use crate::relational::value::{OidRow, OidValue};
+
+        // Each row is a single string of `n` bytes, so its estimated size is `n`.
+        fn row_of(n: usize) -> OidRow {
+            vec![OidValue::String("x".repeat(n))].into_iter().collect()
+        }
+
+        // Empty input yields no slices.
+        assert!(byte_bounded_slices(&[], 1024).is_empty());
+
+        // Five 100-byte rows with a 250-byte cap pack as 2 + 2 + 1.
+        let rows: Vec<OidRow> = (0..5).map(|_| row_of(100)).collect();
+        let slices = byte_bounded_slices(&rows, 250);
+        let lens: Vec<usize> = slices.iter().map(|s| s.len()).collect();
+        assert_eq!(lens, vec![2, 2, 1]);
+        // No data lost, and no slice exceeds the cap.
+        assert_eq!(slices.iter().map(|s| s.len()).sum::<usize>(), rows.len());
+        for s in &slices {
+            assert!(s.iter().map(estimate_row_bytes).sum::<usize>() <= 250);
+        }
+
+        // A single row larger than the cap still makes progress as its own slice.
+        let big = vec![row_of(1000)];
+        let slices = byte_bounded_slices(&big, 250);
+        assert_eq!(slices.len(), 1);
+        assert_eq!(slices[0].len(), 1);
+    }
+
     #[test]
     fn clamp_record_batch_construction() {
         use crate::parquet::schema::clamp_arrow_schema;
```
