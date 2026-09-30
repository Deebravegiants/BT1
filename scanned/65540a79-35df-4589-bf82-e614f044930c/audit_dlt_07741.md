# [?] fix(rocksdb): set max_open_files to prevent fd exhaustion (#22005)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-02-09
Source: https://github.com/paradigmxyz/reth/commit/366857559bede3437e08fce7e4d906f38690aad4
Type: security-commit

## Details
fix(rocksdb): set max_open_files to prevent fd exhaustion (#22005)

Co-authored-by: Amp <amp@ampcode.com>

## Patch
### crates/storage/provider/src/providers/rocksdb/provider.rs
```diff
@@ -111,6 +111,15 @@ const DEFAULT_BLOCK_SIZE: usize = 16 * 1024;
 /// Default max background jobs for `RocksDB` compaction and flushing.
 const DEFAULT_MAX_BACKGROUND_JOBS: i32 = 6;
 
+/// Default max open file descriptors for `RocksDB`.
+///
+/// Caps the number of SST file handles `RocksDB` keeps open simultaneously.
+/// Set to 512 to stay within the common default OS `ulimit -n` of 1024,
+/// leaving headroom for MDBX, static files, and other I/O.
+/// `RocksDB` uses an internal table cache and re-opens files on demand,
+/// so this has negligible performance impact on read-heavy workloads.
+const DEFAULT_MAX_OPEN_FILES: i32 = 512;
+
 /// Default bytes per sync for `RocksDB` WAL writes (1 MB).
 const DEFAULT_BYTES_PER_SYNC: u64 = 1_048_576;
 
@@ -203,6 +212,8 @@ impl RocksDBBuilder {
 
         options.set_log_level(log_level);
 
+        options.set_max_open_files(DEFAULT_MAX_OPEN_FILES);
+
         // Delete obsolete WAL files immediately after all column families have flushed.
         // Both set to 0 means "delete ASAP, no archival".
         options.set_wal_ttl_seconds(0);
```
