# [?] Remove ignored `RUSTSEC-2021-0145`, it does not affect current ckb

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-04-22
Source: https://github.com/nervosnetwork/ckb/commit/61022501077d989e234d2330ef5f6a4235be0a91
Type: security-commit

## Details
Remove ignored `RUSTSEC-2021-0145`, it does not affect current ckb

## Patch
### deny.toml
```diff
@@ -4,8 +4,6 @@ unmaintained = "warn"
 yanked = "deny"
 notice = "deny"
 ignore = [
-    # waiting https://github.com/bheisler/criterion.rs/pull/628 bump release
-    "RUSTSEC-2021-0145",
     # The CVE can be kept under control for its triggering.
     # See https://github.com/launchbadge/sqlx/pull/2455#issuecomment-1507657825 for more information.
     # Meanwhile, awaiting SQLx's new version (> 0.7.3) for full support of any DB driver.
```
