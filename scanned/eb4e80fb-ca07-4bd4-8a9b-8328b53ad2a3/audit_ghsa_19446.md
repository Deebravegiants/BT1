# [C] RoadRunner is at risk of HTTP Request/Response Smuggling through vulnerable dependency

## Summary
Severity: Critical
Advisory: GHSA-g9pc-8g42-g6vq
CVE: CVE-2025-22871
CWE: CWE-1395, CWE-444
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-g9pc-8g42-g6vq
Type: github-advisory

## Affected
- Packagist: `spiral/roadrunner` — affected >=0 <2025.1.0

## Details
The net/http package dependency used by RoadRunner improperly accepts a bare LF as a line terminator in chunked data chunk-size lines. This can permit request smuggling if a net/http server is used in conjunction with a server that incorrectly accepts a bare LF as part of a chunk-ext.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22871
- https://github.com/roadrunner-server/roadrunner/issues/2166
- https://github.com/roadrunner-server/roadrunner/commit/f269279ee87d0b88127741cad1042389af7605fa
- https://cert-portal.siemens.com/productcert/html/ssa-783943.html
- https://github.com/roadrunner-server/roadrunner
- https://github.com/roadrunner-server/roadrunner/releases/tag/v2025.1.0
- https://go.dev/cl/652998
- https://go.dev/issue/71988
- https://groups.google.com/g/golang-announce/c/Y2uBTVKjBQk
- https://pkg.go.dev/vuln/GO-2025-3563
- http://www.openwall.com/lists/oss-security/2025/04/04/4
