# [?] ci: skip RUSTSEC-2021-0013 temporarily

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-01-25
Source: https://github.com/nervosnetwork/ckb/commit/a267accd4697f2a0895dc18f5fd152a6bc512831
Type: security-commit

## Details
ci: skip RUSTSEC-2021-0013 temporarily

## Patch
### deny.toml
```diff
@@ -10,6 +10,7 @@ ignore = [
                          #      Could be removed after heim 0.1.0 released.
     "RUSTSEC-2020-0095", # TODO difference is unmaintained
                          #      It is introduced by pretty_assertions and we only use it in one unit test.
+    "RUSTSEC-2021-0013", # TODO We did not use heim-virt to get cpu information
 ]
 
 [licenses]
```
