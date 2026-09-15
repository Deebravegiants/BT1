# [H] easy-static-server vulnerable to Directory Traversal

## Summary
Severity: High
Advisory: GHSA-wcwm-c3mr-pxcr
CVE: CVE-2022-25931
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-20
Source: https://github.com/advisories/GHSA-wcwm-c3mr-pxcr
Type: github-advisory

## Affected
- npm: `easy-static-server` — affected >=0

## Details
All versions of package easy-static-server are vulnerable to Directory Traversal due to missing input sanitization and sandboxes being employed to the `req.url` user input that is passed to the server code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25931
- https://gist.github.com/lirantal/fdfbe26561788c8194a54bf6d31772c9
- https://github.com/cunjieliu/easyServer
- https://github.com/cunjieliu/easyServer/blob/master/index.js#23L27
- https://security.snyk.io/vuln/SNYK-JS-EASYSTATICSERVER-3153539
