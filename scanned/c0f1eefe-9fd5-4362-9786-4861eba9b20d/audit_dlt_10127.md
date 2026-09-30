# [?] Ignore RUSTSEC-2024-0370 : https://rustsec.org/advisories/RUSTSEC-2024-0370

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-09-12
Source: https://github.com/nervosnetwork/ckb/commit/7880c819316b7993a7bf7fdfe055c290969f6182
Type: security-commit

## Details
Ignore RUSTSEC-2024-0370 : https://rustsec.org/advisories/RUSTSEC-2024-0370

## Patch
### deny.toml
```diff
@@ -79,7 +79,10 @@ ignore = [
   "RUSTSEC-2022-0090",
 # https://rustsec.org/advisories/RUSTSEC-2024-0336
 # `rustls::ConnectionCommon::complete_io` could fall into an infinite loop based on network input
-  "RUSTSEC-2024-0336"
+  "RUSTSEC-2024-0336",
+# Advisory: https://rustsec.org/advisories/RUSTSEC-2024-0370
+# proc-macro-error's maintainer seems to be unreachable, with no commits for 2 years, no releases pushed for 4 years, and no activity on the GitLab repo or response to email.
+  "RUSTSEC-2024-0370"
 #"RUSTSEC-0000-0000",
 #{ id = "RUSTSEC-0000-0000", reason = "you can specify a reason the advisory is ignored" },
 #"a-crate-that-is-yanked@0.1.1", # you can also ignore yanked crate versions if you wish
```
