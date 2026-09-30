# [?] *: Check for security vulnerabilities on build

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2020-11-09
Source: https://github.com/graphprotocol/graph-node/commit/173587c87b8ac292f1bcf9b0aeae987dfc325b50
Type: security-commit

## Details
*: Check for security vulnerabilities on build

## Patch
### .travis.yml
```diff
@@ -1,5 +1,6 @@
 dist: bionic
 language: rust
+cache: cargo # cache cargo-audit once installed
 rust:
   - stable
   - beta
@@ -66,10 +67,12 @@ env:
 
 # Test pipeline
 before_script:
+  - cargo install --force cargo-audit
   - psql -c "ALTER USER travis WITH PASSWORD 'travis';"
   - psql -c 'create database graph_node_test;' -U travis
 
 script:
+  - cargo audit
   # Run tests
   - ipfs daemon &> /dev/null &
   - RUST_BACKTRACE=1 cargo test --verbose --all -- --nocapture
```
