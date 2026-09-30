# [H] lite-dev-server vulnerable to Directory Traversal

## Summary
Severity: High
Advisory: GHSA-pppv-ch8p-rp2w
CVE: CVE-2022-25895
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-pppv-ch8p-rp2w
Type: github-advisory

## Affected
- npm: `lite-dev-server` — affected >=0

## Details
All versions of package lite-dev-server are vulnerable to Directory Traversal due to missing input sanitization and sandboxes being employed to the `req.url` user input that is passed to the server code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25895
- https://gist.github.com/lirantal/0f8a48c3f5ac581ce73123abe9f7f120
- https://github.com/shadowwzw/lite-dev-server
- https://github.com/shadowwzw/lite-dev-server/blob/master/src/server.js#23L134
- https://security.snyk.io/vuln/SNYK-JS-LITEDEVSERVER-3153718
