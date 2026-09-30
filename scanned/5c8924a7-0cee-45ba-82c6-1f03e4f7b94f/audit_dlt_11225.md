# [?] chore: ignore quick-xml RUSTSEC-2026-0194/0195 advisories (#13257)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-07-06
Source: https://github.com/noir-lang/noir/commit/138d0f21a27a321b0ba13910c77337a5d6832834
Type: security-commit

## Details
chore: ignore quick-xml RUSTSEC-2026-0194/0195 advisories (#13257)

Co-authored-by: Claude Fable 5 <noreply@anthropic.com>

## Patch
### deny.toml
```diff
@@ -8,6 +8,12 @@ yanked = "warn"
 ignore = [
     "RUSTSEC-2024-0388", # derivative unmaintained
     "RUSTSEC-2024-0436", # paste unmaintained
+    # quick-xml DoS on attacker-controlled XML (quadratic attribute checks / unbounded
+    # namespace allocations). Only reachable via inferno's flamegraph handling in
+    # noir_profiler and pprof, which never parse untrusted XML. No inferno release on a
+    # fixed quick-xml (>= 0.41.0) exists yet; drop these once one does.
+    "RUSTSEC-2026-0194",
+    "RUSTSEC-2026-0195",
 ]
 
 # This section is considered when running `cargo deny check bans`.
```
