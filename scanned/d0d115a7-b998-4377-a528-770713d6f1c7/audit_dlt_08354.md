# [?] cargo-deny: allow RUSTSEC-2024-0421 while we wait for passkey-client to update

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2024-12-11
Source: https://github.com/MystenLabs/sui/commit/8dcc3c13f1353cf960615ed2b197ce948750b203
Type: security-commit

## Details
cargo-deny: allow RUSTSEC-2024-0421 while we wait for passkey-client to update

## Patch
### deny.toml
```diff
@@ -43,6 +43,8 @@ ignore = [
     "RUSTSEC-2024-0384",
     # allow unmaintained derivative crate used in transitive dependencies (ark-*)
     "RUSTSEC-2024-0388",
+    # allow outdated 'idna' until passkey-client crate is able to update
+    "RUSTSEC-2024-0421",
 ]
 # Threshold for security vulnerabilities, any vulnerability with a CVSS score
 # lower than the range specified will be ignored. Note that ignored advisories
```
