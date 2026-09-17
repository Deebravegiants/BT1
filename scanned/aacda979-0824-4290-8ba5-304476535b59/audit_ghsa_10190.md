# [H] Weblate: Remote code execution during backup restoration

## Summary
Severity: High
Advisory: GHSA-558g-h753-6m33
CVE: CVE-2026-33435
CWE: CWE-23, CWE-434, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-558g-h753-6m33
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.17

## Details
### Impact
The project backup didn't filter Git and Mercurial configuration files and this could lead to remote code execution under certain circumstances.

### Patches
* https://github.com/WeblateOrg/weblate/pull/18549

### Workarounds
The project backup is only accessible to users who can create projects. Restricting access to this limits scope of the vulnerability.

### References
This issue was reported by [ggamno](https://hackerone.com/ggamno) via HackerOne.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-558g-h753-6m33
- https://nvd.nist.gov/vuln/detail/CVE-2026-33435
- https://github.com/WeblateOrg/weblate/pull/18549
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2026-154.yaml
