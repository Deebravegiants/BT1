# [C] FUXA has JWT Authentication Bypass via HTTP Referer header spoofing

## Summary
Severity: Critical
Advisory: GHSA-4r4r-4jp4-wwf9
CVE: CVE-2025-69985
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-4r4r-4jp4-wwf9
Type: github-advisory

## Affected
- npm: `@frangoteam/fuxa` — affected >=0

## Details
FUXA 1.2.8 and prior contains an Authentication Bypass vulnerability leading to Remote Code Execution (RCE). The vulnerability exists in the server/api/jwt-helper.js middleware, which improperly trusts the HTTP "Referer" header to validate internal requests. A remote unauthenticated attacker can bypass JWT authentication by spoofing the Referer header to match the server's host. Successful exploitation allows the attacker to access the protected /api/runscript endpoint and execute arbitrary Node.js code on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69985
- https://gist.github.com/lihy10/8cb2dd65ebf1385f12a7e00e25a50d40
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/blob/master/server/api/jwt-helper.js
