# [M] Weblate Vulnerable to Private Translation Enumeration via Screenshot API

## Summary
Severity: Medium
Advisory: GHSA-gcg5-86jr-f7jg
CVE: CVE-2026-44263
CWE: CWE-203
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-gcg5-86jr-f7jg
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.17.1

## Details
### Impact

The screenshots, tasks, and component link API allowed for the enumeration of translations in a project inaccessible to the user.

### Patches
* https://github.com/WeblateOrg/weblate/pull/19258

### Acknowledgement
Weblate thanks Luay for reporting this vulnerability according to the organization's [security issues guideline](https://docs.weblate.org/en/latest/security/issues.html).

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-gcg5-86jr-f7jg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44263
- https://github.com/WeblateOrg/weblate/pull/19258
- https://github.com/WeblateOrg/weblate/commit/6cf892c7bd50b667a65a99d716a90694f7d9f203
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-5.17.1
