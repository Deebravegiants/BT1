# [?] chore: Allow `RUSTSEC-2025-0055` (#8447)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-09-03
Source: https://github.com/iotaledger/iota/commit/8faaf1c8e5494bd846da5b78ad79a3b79f6cae08
Type: security-commit

## Details
chore: Allow `RUSTSEC-2025-0055` (#8447)

# Description of change

Update `tracing-subscriber` to avoid
[`RUSTSEC-2025-0055`](https://rustsec.org/advisories/RUSTSEC-2025-0055).

## Patch
### deny.toml
```diff
@@ -55,6 +55,8 @@ ignore = [
   "RUSTSEC-2024-0436",
   # backoff is unmaintained
   "RUSTSEC-2025-0012",
+  # Logging user input may result in poisoning logs with ANSI escape sequences
+  "RUSTSEC-2025-0055",
 ]
 # Threshold for security vulnerabilities, any vulnerability with a CVSS score
 # lower than the range specified will be ignored. Note that ignored advisories
```

### external-crates/move/deny.toml
```diff
@@ -54,6 +54,8 @@ ignore = [
   "RUSTSEC-2024-0384",
   # `paste` is unmaintained
   "RUSTSEC-2024-0436",
+  # Logging user input may result in poisoning logs with ANSI escape sequences
+  "RUSTSEC-2025-0055",
 ]
 # Threshold for security vulnerabilities, any vulnerability with a CVSS score
 # lower than the range specified will be ignored. Note that ignored advisories
```
