# [C] Anchor CMS Logs Credentials

## Summary
Severity: Critical
Advisory: GHSA-hxcw-pqqc-rv85
CVE: CVE-2018-7251
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hxcw-pqqc-rv85
Type: github-advisory

## Affected
- Packagist: `anchorcms/anchor-cms` — affected >=0 <0.12.7

## Details
An issue was discovered in `config/error.php` in Anchor 0.12.3. The error log is exposed at an errors.log URI, and contains MySQL credentials if a MySQL error (such as "Too many connections") has occurred.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7251
- https://github.com/anchorcms/anchor-cms/issues/1247
- https://github.com/anchorcms/anchor-cms
- https://github.com/anchorcms/anchor-cms/releases/tag/0.12.7
- https://twitter.com/finnwea/status/965279233030393856
- http://packetstormsecurity.com/files/154723/Anchor-CMS-0.12.3a-Information-Disclosure.html
- http://www.andmp.com/2018/02/advisory-assigned-CVE-2018-7251-in-anchorcms.html
