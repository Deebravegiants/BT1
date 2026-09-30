# [?] Ignore vulnerability in hyper (#2188)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2021-02-08
Source: https://github.com/sigp/lighthouse/commit/194609d210b6d51d5d07abea05bfab38fa755262
Type: security-commit

## Details
Ignore vulnerability in hyper (#2188)

## Issue Addressed

NA

## Proposed Changes

Ignores a [hyper vuln](https://rustsec.org/advisories/RUSTSEC-2021-0020) that will be fixed in #2172.

I am comfortable with ignoring this because we have a fix in the works and the impact of the vuln is low to negligible.   

## Additional Info

NA

## Patch
### Makefile
```diff
@@ -137,7 +137,7 @@ arbitrary-fuzz:
 audit:
 	cargo install --force cargo-audit
 	# TODO: we should address this --ignore.
-	cargo audit --ignore RUSTSEC-2016-0002 --ignore RUSTSEC-2020-0008 --ignore RUSTSEC-2017-0002
+	cargo audit --ignore RUSTSEC-2016-0002 --ignore RUSTSEC-2020-0008 --ignore RUSTSEC-2017-0002 --ignore RUSTSEC-2021-0020
 
 # Runs `cargo udeps` to check for unused dependencies
 udeps:
```
