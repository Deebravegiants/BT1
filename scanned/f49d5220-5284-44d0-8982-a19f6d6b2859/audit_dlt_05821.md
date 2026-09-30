# [?] chore(ci): ignore RUSTSEC-2026-0098 and RUSTSEC-2026-0099 in cargo audit (#15584)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-04-16
Source: https://github.com/near/nearcore/commit/5b7432af644ebe51dea3d11a964223af70ff41ca
Type: security-commit

## Details
chore(ci): ignore RUSTSEC-2026-0098 and RUSTSEC-2026-0099 in cargo audit (#15584)

`cargo audit -D warnings` started failing on master after two new
rustls-webpki advisories were published on 2026-04-14:

- RUSTSEC-2026-0098: name constraints for URI names incorrectly accepted
- RUSTSEC-2026-0099: name constraints accepted for certificates
asserting a wildcard name

Both fixed in `rustls-webpki >= 0.103.12`. Bumped the 0.103.10 instance
in the lockfile to 0.103.12. The 0.102.8 instance comes in via
`object_store 0.13.1 -> reqwest 0.12.4 -> tokio-rustls 0.25.0 -> rustls
0.22.4`, which has no patched 0.102.x release.

Same blocker as the existing RUSTSEC-2026-0049 ignore (`object_store`
still pins `reqwest ^0.12`), so 0098 and 0099 are added to the ignore
list with the same TODO.

## Patch
### .cargo/audit.toml
```diff
@@ -42,6 +42,15 @@ ignore = [
     # TODO(#15435): Update object_store once the maintainers release a version with reqwest 0.13+
     "RUSTSEC-2026-0049",
 
+    # RUSTSEC-2026-0098 and RUSTSEC-2026-0099 describe name-constraint validation bugs in
+    # rustls-webpki (URI names, and certs asserting wildcard names respectively). Same transitive
+    # chain as RUSTSEC-2026-0049 above, and same blocker:
+    # object_store 0.13.1 -> reqwest 0.12.4 -> tokio-rustls 0.25.0 -> rustls 0.22.4 -> rustls-webpki 0.102.8
+    # Fixed in rustls-webpki >= 0.103.12, which requires upgrading the whole rustls stack via object_store.
+    # TODO(#15435): Remove once object_store releases a version with reqwest 0.13+ / rustls 0.23+.
+    "RUSTSEC-2026-0098",
+    "RUSTSEC-2026-0099",
+
     # libsecp256k1 is unmaintained, but every version of aurora-engine-transactions pulls it in
     # (via aurora-engine-precompiles in 1.1, or aurora-engine-sdk in 1.2+). In the main workspace
     # it's only a dev-dependency (test-loop-tests, integration-tests). It is also a transitive
```

### Cargo.lock
```diff
@@ -7430,7 +7430,7 @@ dependencies = [
  "aws-lc-rs",
  "once_cell",
  "rustls-pki-types",
- "rustls-webpki 0.103.10",
+ "rustls-webpki 0.103.12",
  "subtle",
  "zeroize",
 ]
@@ -7502,7 +7502,7 @@ dependencies = [
  "rustls 0.23.28",
  "rustls-native-certs 0.8.3",
  "rustls-platform-verifier-android",
- "rustls-webpki 0.103.10",
+ "rustls-webpki 0.103.12",
  "security-framework 3.7.0",
  "security-framework-sys",
  "webpki-root-certs",
@@ -7528,9 +7528,9 @@ dependencies = [
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.10"
+version = "0.103.12"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "df33b2b81ac578cabaf06b89b0631153a3f416b0a886e8a7a1707fb51abbd1ef"
+checksum = "8279bb85272c9f10811ae6a6c547ff594d6a7f3c6c6b02ee9726d1d0dcfcdd06"
 dependencies = [
  "aws-lc-rs",
  "ring",
```
