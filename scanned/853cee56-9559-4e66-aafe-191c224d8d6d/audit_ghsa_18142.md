# [M] Memos Vulnerable to Stored Cross-Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-cgrg-86m5-xm4w
CVE: CVE-2025-56761
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-cgrg-86m5-xm4w
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0

## Details
Memos 0.22 is vulnerable to Stored Cross site scripting (XSS) vulnerabilities by the upload attachment and user avatar features. Memos does not verify the content type of the uploaded data and serve it back as is. An authenticated attacker can use this to elevate their privileges when the stored XSS is viewed by an admin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56761
- https://github.com/usememos/memos
- https://github.com/usememos/memos/blob/v0.24.0/server/router/api/v1/user_service.go#L147
- https://github.com/usememos/memos/blob/v0.24.4/server/router/api/v1/resource_service.go#L48
- https://www.sonarsource.com/blog/securing-go-applications-with-sonarqube-real-world-examples
