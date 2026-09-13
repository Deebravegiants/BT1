# [H] uutils coreutils: cp/install/mv/ln --suffix alone does not enable backup mode (silent data loss vs GNU)

## Summary
Severity: High
Advisory: GHSA-fqf6-gxhh-2xhw
CWE: CWE-440, CWE-693
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-fqf6-gxhh-2xhw
Type: github-advisory

## Affected
- crates.io: `uucore` — affected >=0 <0.6.0

## Details
`determine_backup_mode` in `src/uucore/src/lib/features/backup_control.rs` only checks `--backup`/`-b` and returns `BackupMode::None` when only `--suffix` is given. GNU enables backup mode when `--suffix` is used alone (defaulting to existing/numbered, or `$VERSION_CONTROL`). Affects `cp`, `install`, `mv`, `ln` which share this code.

```
# uutils: no backup created
$ coreutils cp --suffix=.bak src dest      # dest.bak NOT created
# GNU: dest.bak created
$ cp --suffix=.bak src dest
```

**Impact:** users/scripts relying on `--suffix` to back up a file before overwrite get silent data loss; breaks GNU compatibility across four utilities. Recommendation: enable backup mode when `--suffix` is present.

_Note: this is primarily a GNU-compatibility/data-safety divergence rather than a classic exploitable vulnerability — review whether it warrants a CVE._

**Remediation:** Acknowledged by Canonical; fixed in PR #9741 (`uucore: use --suffix to enable backup mode`), commit `939ab037a`, merged 2025-12-21. `determine_backup_mode` now has a `--suffix`-alone branch that resolves the mode from `$VERSION_CONTROL` (defaulting to `existing`). Released in **uucore 0.6.0** and later (vulnerable: `< 0.6.0`). Regression tests added in the same file: `test_backup_mode_suffix_without_backup_option` and `test_backup_mode_suffix_without_backup_option_with_env_var`.

---
_Reported by Zellic in the *uutils coreutils Program Security Assessment* (prepared for Canonical, Jan 20 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`. Finding 3.7. Credit: Zellic._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-fqf6-gxhh-2xhw
- https://github.com/uutils/coreutils/pull/9741
- https://github.com/uutils/coreutils
