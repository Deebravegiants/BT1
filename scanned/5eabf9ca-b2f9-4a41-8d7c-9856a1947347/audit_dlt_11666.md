# [?] chore(doc): add GH security advisory link on SECURITY.md

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2026-08-05
Source: https://github.com/bitcoindevkit/bdk/commit/a98ab189340c6ed2a2fbc91ee6d8178950e09b6b
Type: security-commit

## Details
chore(doc): add GH security advisory link on SECURITY.md

## Patch
### README.md
```diff
@@ -49,6 +49,10 @@ The [`bdk_wallet`] repository and crate contains a higher level `Wallet` type th
 [`bdk_chain`]: https://docs.rs/bdk-chain/
 [`bdk_wallet`]: https://github.com/bitcoindevkit/bdk_wallet
 
+## Security Policy
+
+To report a security issue, please refer to the [security policy](SECURITY.md).
+
 ## Minimum Supported Rust Version (MSRV)
 
 The following BDK crates maintains a MSRV of 1.85.0. To build these crates with the MSRV of 1.85.0 you will need to pin dependencies by running the [`pin-msrv.sh`](./ci/pin-msrv.sh) script.
```

### SECURITY.md
```diff
@@ -1,8 +1,12 @@
 # Security Policy
 
-To report security issues send an email to `security AT bitcoindevkit DOT org` (not for support).
+To report security issues, either
 
-The following key may be used to communicate sensitive information to developers:
+- send an email to `security AT bitcoindevkit DOT org` (not for support), or
+- open a security advisory on GitHub at
+[`https://github.com/bitcoindevkit/bdk/security/advisories`](https://github.com/bitcoindevkit/bdk/security/advisories).
+
+The following key may be used to communicate sensitive information to BDK via email:
 
 | Name | Fingerprint |
 | ---- | ----------- |
```
