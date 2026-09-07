# [M] rocksdb vulnerable to out-of-bounds read

## Summary
Severity: Medium
Advisory: GHSA-xpp3-xrff-w6rh
Ecosystem: crates.io
Published: 2022-08-12
Source: https://github.com/advisories/GHSA-xpp3-xrff-w6rh
Type: github-advisory

## Affected
- crates.io: `rocksdb` — affected >=0 <0.19.0

## Details
Affected versions of this crate called the RocksDB C API
`rocksdb_open_column_families_with_ttl()` with a pointer to a single integer
TTL value, but one TTL value for each column family is expected.

This is only relevant when using
`rocksdb::DBWithThreadMode::open_cf_descriptors_with_ttl()` with multiple
column families.

This bug has been fixed in v0.19.0.

## References
- https://github.com/rust-rocksdb/rust-rocksdb/pull/616
- https://github.com/rust-rocksdb/rust-rocksdb
- https://github.com/rust-rocksdb/rust-rocksdb/releases/tag/v0.19.0
- https://rustsec.org/advisories/RUSTSEC-2022-0046.html
