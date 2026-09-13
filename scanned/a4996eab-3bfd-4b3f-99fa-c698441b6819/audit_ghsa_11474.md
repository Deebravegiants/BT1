# [M] OpenClaw: Exec approval allowlist patterns overmatched on POSIX paths

## Summary
Severity: Medium
Advisory: GHSA-f8r2-vg7x-gh8m
CWE: CWE-178, CWE-625
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-f8r2-vg7x-gh8m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
### Summary

`matchesExecAllowlistPattern` normalized patterns and targets with lowercasing and compiled glob matching too broadly on POSIX. In addition, the `?` wildcard could match `/`, which allowed matches to cross path segments.

### Impact

These matching rules could overmatch allowlist entries and permit commands or executable paths that an operator did not intend to approve.

### Affected versions

`openclaw` `<= 2026.3.8`

### Patch

Fixed in `openclaw` `2026.3.11` and included in later releases such as `2026.3.12`. Exec allowlist matching now respects the intended path semantics, and regression tests cover the POSIX case-folding and slash-crossing cases.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f8r2-vg7x-gh8m
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
