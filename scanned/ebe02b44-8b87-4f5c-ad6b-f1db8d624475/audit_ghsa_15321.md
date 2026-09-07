# [H] memos CORS Misconfiguration in server.go (GHSL-2024-034)

## Summary
Severity: High
Advisory: GHSA-p4fx-qf2h-jpmj
CVE: CVE-2024-41659
CWE: CWE-942
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-p4fx-qf2h-jpmj
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.21.0

## Details
memos is a privacy-first, lightweight note-taking service. A CORS misconfiguration exists in memos 0.20.1 and earlier where an arbitrary origin is reflected with Access-Control-Allow-Credentials set to true. This may allow an attacking website to make a cross-origin request, allowing the attacker to read private information or make privileged changes to the system as the vulnerable user account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41659
- https://github.com/usememos/memos/commit/8101a5e0b162044c16385bee4f12a4a653d050b9
- https://github.com/usememos/memos
- https://github.com/usememos/memos/blob/v0.20.1/server/server.go#L163
- https://securitylab.github.com/advisories/GHSL-2024-034_memos
