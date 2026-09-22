# [H] Denial of Service vulnerability in lite-web-server

## Summary
Severity: High
Advisory: GHSA-8237-3q5g-99fv
CVE: CVE-2023-26104
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-25
Source: https://github.com/advisories/GHSA-8237-3q5g-99fv
Type: github-advisory

## Affected
- npm: `lite-web-server` — affected >=0

## Details
All versions of the package lite-web-server are vulnerable to Denial of Service (DoS) when an attacker sends an HTTP request and includes control characters that the decodeURI() function is unable to parse.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26104
- https://gist.github.com/lirantal/637520812da06fffb91dd86d02ff6bde
- https://github.com/chasyumen/lite-web-server
- https://github.com/chasyumen/lite-web-server/blob/main/src/WebServer.js#23L274
- https://security.snyk.io/vuln/SNYK-JS-LITEWEBSERVER-3153703
