# [M] Weblate: Improper access control for the translation memory in API

## Summary
Severity: Medium
Advisory: GHSA-mpf5-3vph-q75r
CVE: CVE-2026-33214
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-mpf5-3vph-q75r
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.17

## Details
### Impact
The translation memory API exposed unintended endpoints, which in turn didn't do proper access control.

### Patches
* https://github.com/WeblateOrg/weblate/pull/18513

### Workarounds
Blocking access to `/api/memory/` in the HTTP server removes access to this feature.

### References
This issue was reported by [ggamno](https://hackerone.com/ggamno) via HackerOne.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-mpf5-3vph-q75r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33214
- https://github.com/WeblateOrg/weblate/pull/18513
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2026-152.yaml
