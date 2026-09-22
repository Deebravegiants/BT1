# [H] Predictable password reset token may lead to account takeover in countly-server

## Summary
Severity: High
Advisory: CVE-2022-29174
Aliases: GHSA-98vh-wqw5-p23v
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-17
Source: https://osv.dev/vulnerability/CVE-2022-29174
Type: osv

## Details
countly-server is the server-side part of Countly, a product analytics solution. Prior to versions 22.03.7 and 21.11.4, a malicious actor who knows an account email address/username and full name specified in the database is capable of guessing the password reset token. The actor may use this information to reset the password and take over the account. The problem has been patched in Countly Server version 22.03.7 for servers using the new user interface and in 21.11.4 for servers using the old user interface.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29174.json
- https://github.com/Countly/countly-server/security/advisories/GHSA-98vh-wqw5-p23v
- https://nvd.nist.gov/vuln/detail/CVE-2022-29174
- https://github.com/Countly/countly-server/commit/2bfa1ee1fa46e9bb007cf8687ad197ab9c604999
