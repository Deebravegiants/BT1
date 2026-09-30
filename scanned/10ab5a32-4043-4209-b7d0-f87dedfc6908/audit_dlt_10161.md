# [?] ci: skip RUSTSEC-2020-0077 temporarily

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2020-12-02
Source: https://github.com/nervosnetwork/ckb/commit/86b9425042b85e41af910bc2755ad194475e8136
Type: security-commit

## Details
ci: skip RUSTSEC-2020-0077 temporarily

## Patch
### deny.toml
```diff
@@ -8,6 +8,7 @@ ignore = [
     "RUSTSEC-2020-0036", # TODO failure is officially deprecated/unmaintained, but still a lot of required crates are dependent on it
     "RUSTSEC-2020-0043", # TODO ws allows remote attacker to run the process out of memory, since it is no longer actively maintained, we couldn't fix it in the short term
     "RUSTSEC-2020-0056", # We did not use the `stdweb` library, only `wasm32-unknown-unknown` would use `getrandom` and `wasm-bindgen`, `stdweb` would only be used in cargo-web
+    "RUSTSEC-2020-0077", # TODO memmap is unmaintained, but ckb-vm is dependent on it, so we allow it temporarily
 ]
 
 [licenses]
```
