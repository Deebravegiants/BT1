# [C] CubeCart: Authenticated Arbitrary File Upload to RCE in REST Files API

## Summary
Severity: Critical
Advisory: CVE-2026-45053
Aliases: GHSA-652f-8c88-25cx
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-45053
Type: osv

## Details
CubeCart is an ecommerce software solution. Prior to 6.7.0, an Authenticated Arbitrary File Upload vulnerability exists in the REST API File Manager endpoint (POST /api/v1/files) of CubeCart. The endpoint allows any holder of an API key with files:rw permission to upload PHP source files into the web-accessible images/source/ directory, where they are executed by the web server. Combined with a path-traversal flaw in the same endpoint's filepath parameter, a single API request writes a webshell anywhere the webserver process can write — including the document root — yielding full Remote Code Execution. This vulnerability is fixed in 6.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45053.json
- https://github.com/cubecart/v6/security/advisories/GHSA-652f-8c88-25cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45053
