# [?] Update bytes to 1.11.1 (RUSTSEC-2026-0007).

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-04-15
Source: https://github.com/zcash/zcash/commit/59b5784294d3e7872ce9436d4a625a95edb1ba3b
Type: security-commit

## Details
Update bytes to 1.11.1 (RUSTSEC-2026-0007).

Fix integer overflow in BytesMut::reserve that could cause
out-of-bounds memory access. Only affects the optional Prometheus
metrics exporter when enabled via -prometheusport. On platforms
with 64-bit usize, triggering the overflow would require a request
large enough to overflow 2^64, which is not practically achievable.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -313,9 +313,9 @@ checksum = "1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b"
 
 [[package]]
 name = "bytes"
-version = "1.7.2"
+version = "1.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "428d9aa8fbc0670b7b8d6030a7fadd0f86151cae55e4dbbece15f3780a3dfaf3"
+checksum = "1e748733b7cbc798e1434b6ac524f0c1ff2ab456fe201501e6497c8417a4fc33"
 
 [[package]]
 name = "cbc"
```

### qa/supply-chain/audits.toml
```diff
@@ -334,6 +334,12 @@ who = "Jack Grigg <jack@electriccoin.co>"
 criteria = "safe-to-deploy"
 delta = "1.7.1 -> 1.7.2"
 
+[[audits.bytes]]
+who = "Daira-Emma Hopwood <daira@jacaranda.org>"
+criteria = "safe-to-deploy"
+delta = "1.7.2 -> 1.11.1"
+notes = "New/changed uses of unsafe are documented and seem plausible."
+
 [[audits.cc]]
 who = "Daira-Emma Hopwood <daira@jacaranda.org>"
 criteria = "safe-to-deploy"
```
