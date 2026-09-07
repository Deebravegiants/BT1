# [H] Concrete CMS is vulnerable to Stored XSS via OAuth integration name

## Summary
Severity: High
Advisory: GHSA-h72c-xx3w-w8h7
CVE: CVE-2026-8197
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-h72c-xx3w-w8h7
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to Stored XSS via OAuth integration name. The OAuth authorize template renders the integration name (admin-controlled) through Concrete's t() translation helper as a sprintf-style format. The <strong>...</strong> wrap is built by PHP string interpolation before t() runs, so the integration name lands in the translated output as raw HTML. A rogue admin could potentially snoop on login submissions.The Concrete CMS security team thanks Yonatan Drori (Tenzai) for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8197
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
