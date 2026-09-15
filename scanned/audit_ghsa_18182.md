# [M] Memos Vulnerable to Path Traversal via the CreateResource Endpoint

## Summary
Severity: Medium
Advisory: GHSA-78j5-8vq7-jxv5
CVE: CVE-2025-56760
CWE: CWE-24
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-78j5-8vq7-jxv5
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0

## Details
When Memos 0.22 is configured to store objects locally, an attacker can create a file via the CreateResource endpoint containing a path traversal sequence in the name, allowing arbitrary file write on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56760
- https://github.com/usememos/memos
- https://github.com/usememos/memos/blob/v0.24.4/server/router/api/v1/resource_service.go#L48
- https://www.sonarsource.com/blog/securing-go-applications-with-sonarqube-real-world-examples
