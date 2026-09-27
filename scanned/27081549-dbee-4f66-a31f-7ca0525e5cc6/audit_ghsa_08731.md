# [M] Concrete CMS is vulnerable to authorization bypass in the Calendar Block

## Summary
Severity: Medium
Advisory: GHSA-46xh-7854-f568
CVE: CVE-2026-8205
CWE: CWE-425
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-46xh-7854-f568
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to authorization bypass in the Calendar Block since action_get_events does not check canView on the calendar which results in restricted event details being disclosed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8205
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
