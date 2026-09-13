# [H] CodeIgniter Improper Privilege Management

## Summary
Severity: High
Advisory: GHSA-jwqp-wh5g-4gmm
CVE: CVE-2020-10793
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jwqp-wh5g-4gmm
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0

## Details
CodeIgniter through 4.0.0 allows remote attackers to gain privileges via a modified Email ID to the "Select Role of the User" page. NOTE: A contributor to the CodeIgniter framework argues that the issue should not be attributed to CodeIgniter. Furthermore, the blog post reference shows an unknown website built with the CodeIgniter framework but that CodeIgniter is not responsible for introducing this issue because the framework has never provided a login screen, nor any kind of login or user management facilities beyond a Session library. Also, another reporter indicates the issue is with a custom module/plugin to CodeIgniter, not CodeIgniter itself.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10793
- https://codeigniter4.github.io/userguide/extending/authentication.html
- https://github.com/codeigniter4/framework
- https://medium.com/@vbharad/account-takeover-via-modifying-email-id-codeigniter-framework-ca30741ad297
