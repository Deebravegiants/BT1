# [H] Casdoor CORS misconfiguration (GHSL-2024-035)

## Summary
Severity: High
Advisory: GHSA-mchx-7j67-8mcf
CVE: CVE-2024-41657
CWE: CWE-942
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-mchx-7j67-8mcf
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
Casdoor is a UI-first Identity and Access Management (IAM) / Single-Sign-On (SSO) platform. In Casdoor 1.577.0 and earlier, a logic vulnerability exists in the beego filter CorsFilter that allows any website to make cross domain requests to Casdoor as the logged in user. Due to the a logic error in checking only for a prefix when authenticating the Origin header, any domain can create a valid subdomain with a valid subdomain prefix (Ex: localhost.example.com), allowing the website to make requests to Casdoor as the current signed-in user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41657
- https://github.com/casdoor/casdoor
- https://github.com/casdoor/casdoor/blob/v1.577.0/routers/cors_filter.go#L45
- https://securitylab.github.com/advisories/GHSL-2024-035_GHSL-2024-036_casdoor
