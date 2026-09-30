# [?] ci: skip RUSTSEC-2020-0095 temporarily

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-01-07
Source: https://github.com/nervosnetwork/ckb/commit/d48e3c60a0231d5f5c04a31c9a115b568694394d
Type: security-commit

## Details
ci: skip RUSTSEC-2020-0095 temporarily

## Patch
### deny.toml
```diff
@@ -6,9 +6,10 @@ notice = "deny"
 ignore = [
     "RUSTSEC-2020-0016", # TODO net2 has been deprecated, but still a lot of required crates are dependent on it
     "RUSTSEC-2020-0043", # TODO ws allows remote attacker to run the process out of memory, since it is no longer actively maintained, we couldn't fix it in the short term
-    "RUSTSEC-2020-0056", # We did not use the `stdweb` library, only `wasm32-unknown-unknown` would use `getrandom` and `wasm-bindgen`, `stdweb` would only be used in cargo-web
     "RUSTSEC-2020-0082", # TODO ordered_float:NotNan may contain NaN after panic in assignment operators
                          #      Could be removed after heim 0.1.0 released.
+    "RUSTSEC-2020-0095", # TODO difference is unmaintained
+                         #      It is introduced by pretty_assertions and we only use it in one unit test.
 ]
 
 [licenses]
```
