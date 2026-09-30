# [?] overflow protect int cast

## Summary
Severity: Unknown
Chain: MakerDAO
Component: sky-ecosystem/dss
Published: 2018-08-06
Source: https://github.com/sky-ecosystem/dss/commit/b9f0520421ba5dccd5f3820f46b14ac1dbc49644
Type: security-commit

## Details
overflow protect int cast

## Patch
### src/tune.sol
```diff
@@ -46,6 +46,7 @@ contract Vat {
     // --- Fungibility Engine ---
     int256 constant ONE = 10 ** 27;
     function move(address src, address dst, uint wad) public auth {
+        require(int(wad) >= 0);
         move(src, dst, int(wad));
     }
     function move(address src, address dst, int wad) public auth {
```
