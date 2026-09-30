# [?] fix(ci): ignore quick-xml RUSTSEC-2026-0194 and RUSTSEC-2026-0195 until inferno updates (#10899)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-03
Source: https://github.com/ZcashFoundation/zebra/commit/c057c4abcb8f00ac69ff1550d9c9beea6c236f74
Type: security-commit

## Details
fix(ci): ignore quick-xml RUSTSEC-2026-0194 and RUSTSEC-2026-0195 until inferno updates (#10899)

Co-authored-by: Conrado <conrado@zfnd.org>

## Patch
### deny.toml
```diff
@@ -9,12 +9,17 @@
 [advisories]
 version = 2
 yanked = "deny"
-# Unmaintained-crate advisories. Each entry is a transitive dep we can't upgrade
-# yet, or a direct dep. Remove each entry as its dependency chain is upgraded.
+# Ignored advisories. Each entry is a transitive dep we can't upgrade yet, or a
+# direct dep. Remove each entry as its dependency chain is upgraded.
 ignore = [
     "RUSTSEC-2026-0173", # proc-macro-error2 (unmaintained): via librustzcash orchard -> getset
     "RUSTSEC-2025-0119", # number_prefix: transitive via indicatif
     "RUSTSEC-2025-0141", # bincode: direct dependency
+    # quick-xml DoS advisories: via inferno (zebrad's `flamegraph` feature), which has no release
+    # allowing the fixed quick-xml 0.41 yet: https://github.com/jonhoo/inferno/pull/369.
+    # Zebra only feeds inferno locally generated profiling data, never untrusted XML.
+    "RUSTSEC-2026-0194", # quick-xml: quadratic duplicate-attribute check
+    "RUSTSEC-2026-0195", # quick-xml: unbounded namespace-declaration allocation
 ]
 
 # This section is considered when running `cargo deny check licenses`.
```
