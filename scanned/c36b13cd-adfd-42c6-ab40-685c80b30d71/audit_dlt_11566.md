# [?] cargo audit: ignore RUSTSEC-2022-0093

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2023-08-17
Source: https://github.com/velocity-exchange/protocol-v2/commit/c17fab6516de0cff3a035851edcc9f0a8475cf3a
Type: security-commit

## Details
cargo audit: ignore RUSTSEC-2022-0093

## Patch
### .cargo/audit.toml
```diff
@@ -1,7 +1,10 @@
 # RUSTSEC-2022-0013 ignores as upstream dependency
 
 [advisories]
-ignore = ["RUSTSEC-2022-0013"] # advisory IDs to ignore e.g. ["RUSTSEC-2019-0001", ...]
+ignore = [
+	"RUSTSEC-2022-0013",
+	"RUSTSEC-2022-0093", # Double Public Key Signing Function Oracle Attack on `ed25519-dalek`
+]
 informational_warnings = ["unmaintained"] # warn for categories of informational advisories
 severity_threshold = "high" # CVSS severity ("none", "low", "medium", "high", "critical")
 
```
