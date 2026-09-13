# [M] Concrete CMS is vulnerable to unauthenticated page metadata disclosure

## Summary
Severity: Medium
Advisory: GHSA-vpgr-cwfx-pwfw
CVE: CVE-2026-8240
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-vpgr-cwfx-pwfw
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to unauthenticated page metadata disclosure across every page with a configured summary template, revealing the existence of private, draft, and restricted pages while leaking title, path, description, and author information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8240
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
