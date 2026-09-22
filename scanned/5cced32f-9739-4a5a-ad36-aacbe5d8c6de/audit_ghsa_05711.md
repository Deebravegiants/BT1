# [H] Weblate wlc path traversal vulnerability: Unsanitized API slugs in download command 

## Summary
Severity: High
Advisory: GHSA-mmwx-79f6-67jg
CVE: CVE-2026-23535
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-mmwx-79f6-67jg
Type: github-advisory

## Affected
- PyPI: `wlc` — affected >=0 <1.17.2

## Details
### Impact
Multi-translation download could write to an arbitrary location when instructed by a crafted server.

### Patches
* https://github.com/WeblateOrg/wlc/pull/1128

### Workarounds
Do not use `wlc download` with untrusted servers.

### References
This issue was reported to us by [wh1zee](https://hackerone.com/wh1zee) via HackerOne.

## References
- https://github.com/WeblateOrg/wlc/security/advisories/GHSA-mmwx-79f6-67jg
- https://nvd.nist.gov/vuln/detail/CVE-2026-23535
- https://github.com/WeblateOrg/wlc/pull/1128
- https://github.com/WeblateOrg/wlc/commit/216e691c6e50abae97fe2e4e4f21501bf49a585f
- https://github.com/WeblateOrg/wlc
- https://github.com/WeblateOrg/wlc/releases/tag/1.17.2
