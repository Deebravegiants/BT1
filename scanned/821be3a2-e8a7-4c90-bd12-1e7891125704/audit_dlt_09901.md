# [?] fix: manager test was non-deterministic due to mempool fee estimation (#4219)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2023-08-23
Source: https://github.com/iron-fish/ironfish/commit/0bb7033efe9e5408ef9d0eed693261b0bf785db9
Type: security-commit

## Details
fix: manager test was non-deterministic due to mempool fee estimation (#4219)

## Patch
### ironfish/src/mining/manager.test.slow.ts
```diff
@@ -200,7 +200,7 @@ describe('Mining manager', () => {
         node,
         wallet,
         from: accountA,
-        fee: 3n,
+        fee: 20n,
         mints: [
           {
             name: 'Testcoin',
@@ -215,7 +215,7 @@ describe('Mining manager', () => {
         node,
         wallet,
         from: accountA,
-        fee: 2n,
+        fee: 15n,
         mints: [
           {
             name: 'Testcoin',
@@ -232,7 +232,7 @@ describe('Mining manager', () => {
         node,
         wallet,
         from: accountA,
-        fee: 1n,
+        fee: 5n,
         mints: [
           {
             name: 'Testcoin',
```
