# [M] CakePHP: SmtpTransport vulnerable to CRLF header injection

## Summary
Severity: Medium
Advisory: CVE-2026-77634
Aliases: GHSA-2qh5-382h-3jpc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-77634
Type: osv

## Details
CakePHP is a rapid development framework for PHP. Prior to versions 4.5.12, 4.6.5, 5.1.8, 5.2.14, and 5.3.7 on their respective release lines, custom mail headers added with Message::setHeaders() or Message::addHeaders() do not have CRLF bytes removed, allowing header injection when user-controlled data is used in message headers. This issue is fixed in versions 4.5.12, 4.6.5, 5.1.8, 5.2.14, and 5.3.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77634.json
- https://github.com/cakephp/cakephp/security/advisories/GHSA-2qh5-382h-3jpc
- https://nvd.nist.gov/vuln/detail/CVE-2026-77634
- https://github.com/cakephp/cakephp/commit/08188962bcd99a95da1e49f62e786f2d688f1e41
- https://github.com/cakephp/cakephp/commit/2afe42b02d8ddc5d442bca5e8bb61910a727646e
- https://github.com/cakephp/cakephp/commit/3e09dae6cbdc983754fa3a8e6aae74da102a3ea1
- https://github.com/cakephp/cakephp/commit/b67b622457362b075bb37e625a82af73a0b3c9c3
