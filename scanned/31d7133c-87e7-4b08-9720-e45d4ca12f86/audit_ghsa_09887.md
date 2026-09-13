# [M] Weblate: JavaScript localization CDN add-on allows arbitrary local file read outside the repository

## Summary
Severity: Medium
Advisory: GHSA-mqph-7h49-hqfm
CVE: CVE-2026-33220
CWE: CWE-200, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-mqph-7h49-hqfm
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.17

## Details
### Impact
The translation memory API exposed unintended endpoints, which in turn didn't do proper access control.

### Patches
* https://github.com/WeblateOrg/weblate/pull/18516

### Workarounds
The CDN add-on is not enabled by default.

### References
Thanks to @spbavarva for reporting this responsibly via GitHub.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-mqph-7h49-hqfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33220
- https://github.com/WeblateOrg/weblate/pull/18516
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2026-153.yaml
