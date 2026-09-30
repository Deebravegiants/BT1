# [?] chore(rust): ignore RUSTSEC-2026-0118 and RUSTSEC-2026-0119 (#20514)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-05-04
Source: https://github.com/ethereum-optimism/optimism/commit/742987c5fae7fe9574d96296c9738e6a532250a3
Type: security-commit

## Details
chore(rust): ignore RUSTSEC-2026-0118 and RUSTSEC-2026-0119 (#20514)

Both advisories were published 2026-05-01 and affect hickory-proto
<0.26.1, pulled in transitively via reth-network ->
reth-dns-discovery. Ignore in deny.toml until an upstream bump lands.

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### rust/deny.toml
```diff
@@ -14,6 +14,12 @@ ignore = [
   "RUSTSEC-2024-0436",
   # bincode is unmaintained but still functional; transitive dep from reth-nippy-jar and test-fuzz.
   "RUSTSEC-2025-0141",
+  # hickory-proto <0.26.1 NSEC3 closest-encloser DNSSEC validation unbounded loop;
+  # transitive via reth-network -> reth-dns-discovery. Pending upstream bump.
+  "RUSTSEC-2026-0118",
+  # hickory-proto <0.26.1 O(n^2) name-compression CPU exhaustion in BinEncoder;
+  # transitive via reth-network -> reth-dns-discovery. Pending upstream bump.
+  "RUSTSEC-2026-0119",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
