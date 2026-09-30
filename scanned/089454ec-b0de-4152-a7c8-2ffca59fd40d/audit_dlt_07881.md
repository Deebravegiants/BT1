# [?] Fix #3521 (HTTP connection leaks leading to crashes) (#3582)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-04-11
Source: https://github.com/status-im/nimbus-eth2/commit/0304f7b2e63180e39684f87755205e27a987e8e5
Type: security-commit

## Details
Fix #3521 (HTTP connection leaks leading to crashes) (#3582)

## Patch
### vendor/nim-chronos
```diff
@@ -1 +1 @@
-Subproject commit 87197230779002a2bfa8642f0e2ae07e2349e304
+Subproject commit ae2a87778feb5eba556b5f0c619db67ba3fd6710
```

### vendor/nim-json-rpc
```diff
@@ -1 +1 @@
-Subproject commit 9e0a9496c5d5bfd304080f742cce2939ef7bd2ff
+Subproject commit 335f292a5816910aebf215e3a88db8a665133e0e
```
