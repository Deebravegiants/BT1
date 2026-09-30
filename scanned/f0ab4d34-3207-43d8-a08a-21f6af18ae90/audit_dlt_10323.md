# [?] Suppress RUSTSEC-2023-0044 audit failure until SPL upgrades to Solana v1.16.2 or greater (#4586)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2023-06-21
Source: https://github.com/solana-labs/solana-program-library/commit/def28e1a83c2ff58e89645d8481330cc29c837a1
Type: security-commit

## Details
Suppress RUSTSEC-2023-0044 audit failure until SPL upgrades to Solana v1.16.2 or greater (#4586)

## Patch
### ci/do-audit.sh
```diff
@@ -15,5 +15,10 @@ cargo_audit_ignores=(
   # Exception is a stopgap to unblock CI
   # https://github.com/solana-labs/solana/issues/29586
   --ignore RUSTSEC-2023-0001
+
+  # openssl: `openssl` `X509VerifyParamRef::set_host` buffer over-read
+  #
+  # Remove once SPL upgrades to Solana v1.16.2 or greater
+  --ignore RUSTSEC-2023-0044
 )
 cargo +"$rust_stable" audit "${cargo_audit_ignores[@]}"
```
