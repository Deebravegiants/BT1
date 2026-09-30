# [?] Update openssl for CVE-2022-0778 (#3095)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2022-03-17
Source: https://github.com/sigp/lighthouse/commit/a1befd89aaae8bf45d99ddf9cfb4834175069dd4
Type: security-commit

## Details
Update openssl for CVE-2022-0778 (#3095)

## Issue Addressed

Fix the `cargo-audit` failure for the recent openssl bug involving parsing of untrusted certificates (CVE-2022-0778).

## Additional Info

Lighthouse loads remote certificates in the following cases:

* When connecting to an eth1 node (`--eth1-endpoints`).
* When connecting to a beacon node from the VC (`--beacon-nodes`).
* When connecting to a beacon node for checkpoint sync (`--checkpoint-sync-url`).

In all of these cases we are already placing a lot of trust in the server at the other end, however due to the scope for MITM attacks we are still potentially vulnerable. E.g. an ISP could inject an invalid certificate for the remote host which would cause Lighthouse to hang indefinitely.

## Patch
### Cargo.lock
```diff
@@ -4127,9 +4127,9 @@ checksum = "ff011a302c396a5197692431fc1948019154afc178baf7d8e37367442a4601cf"
 
 [[package]]
 name = "openssl-src"
-version = "111.17.0+1.1.1m"
+version = "111.18.0+1.1.1n"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "05d6a336abd10814198f66e2a91ccd7336611f30334119ca8ce300536666fcf4"
+checksum = "7897a926e1e8d00219127dc020130eca4292e5ca666dd592480d72c3eca2ff6c"
 dependencies = [
  "cc",
 ]
```
