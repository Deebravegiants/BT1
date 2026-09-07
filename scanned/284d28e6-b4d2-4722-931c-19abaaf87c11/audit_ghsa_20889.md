# [C] Labstack Echo Open Redirect vulnerability

## Summary
Severity: Critical
Advisory: GHSA-crxj-hrmp-4rwf
CVE: CVE-2022-40083
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-29
Source: https://github.com/advisories/GHSA-crxj-hrmp-4rwf
Type: github-advisory

## Affected
- Go: `github.com/labstack/echo/v4` — affected >=0 <4.9.0

## Details
Labstack Echo v4.8.0 was discovered to contain an open redirect vulnerability via the Static Handler component. This vulnerability can be leveraged by attackers to cause a Server-Side Request Forgery (SSRF). Version 4.9.0 contains a patch for the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40083
- https://github.com/labstack/echo/issues/2259
- https://github.com/labstack/echo/pull/2260
- https://github.com/labstack/echo/pull/2260/commits/3154abd1401554fe4d1c09ec550506d8625fc042
- https://github.com/labstack/echo/commit/0ac4d74402391912ff6da733bb09fd4c3980b4e1
- https://github.com/labstack/echo
- https://github.com/labstack/echo/releases/tag/v4.9.0
- https://pkg.go.dev/vuln/GO-2022-1031
