# [?] ci: skip RUSTSEC-2020-0082 temporarily

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2020-12-07
Source: https://github.com/nervosnetwork/ckb/commit/e414bcb0e78663bf56eba9725a5809667797fb75
Type: security-commit

## Details
ci: skip RUSTSEC-2020-0082 temporarily

## Patch
### deny.toml
```diff
@@ -8,6 +8,8 @@ ignore = [
     "RUSTSEC-2020-0036", # TODO failure is officially deprecated/unmaintained, but still a lot of required crates are dependent on it
     "RUSTSEC-2020-0043", # TODO ws allows remote attacker to run the process out of memory, since it is no longer actively maintained, we couldn't fix it in the short term
     "RUSTSEC-2020-0056", # We did not use the `stdweb` library, only `wasm32-unknown-unknown` would use `getrandom` and `wasm-bindgen`, `stdweb` would only be used in cargo-web
+    "RUSTSEC-2020-0082", # TODO ordered_float:NotNan may contain NaN after panic in assignment operators
+                         #      Could be removed after heim 0.1.0 released.
 ]
 
 [licenses]
```
