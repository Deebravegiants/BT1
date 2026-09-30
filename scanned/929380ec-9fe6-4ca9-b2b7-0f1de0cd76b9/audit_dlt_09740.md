# [?] chore: update bytes to 1.11.1 to fix audit vulnerability

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-02-04
Source: https://github.com/fedimint/fedimint/commit/3e1597845fc21651738a112af9626afc3dbdea34
Type: security-commit

## Details
chore: update bytes to 1.11.1 to fix audit vulnerability

Signed-off-by: Devansh Vashisht <devansh.vashisht.ug24@nsut.ac.in>

## Patch
### Cargo.lock
```diff
@@ -1331,9 +1331,9 @@ checksum = "8f1fe948ff07f4bd06c30984e69f5b4899c516a3ef74f34df92a2df2ab535495"
 
 [[package]]
 name = "bytes"
-version = "1.10.1"
+version = "1.11.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d71b6127be86fdcfddb610f7182ac57211d4b18a3e9c82eb2d17662f2227ad6a"
+checksum = "1e748733b7cbc798e1434b6ac524f0c1ff2ab456fe201501e6497c8417a4fc33"
 
 [[package]]
 name = "bzip2-sys"
```

### Cargo.toml
```diff
@@ -147,7 +147,7 @@ bitcoincore-rpc = "0.19.0"
 bitvec = "1.0.1"
 bls12_381 = "0.8.0"
 bon = "3.6.5"
-bytes = "1.10.1"
+bytes = "1.11.1"
 chacha20poly1305 = "0.10.1"
 chrono = "0.4.41"
 clap = { version = "4.5.41", features = ["derive", "env"] }
```
