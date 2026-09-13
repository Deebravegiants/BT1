# [M] Velocidex Velociraptor has an authorization bypass vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3c93-g9g6-p5j4
CVE: CVE-2026-7573
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-3c93-g9g6-p5j4
Type: github-advisory

## Affected
- Go: `www.velocidex.com/golang/velociraptor` — affected >=0 <0.76.5

## Details
An authorization bypass (CWE-639) in the GetUserRoles gRPC API endpoint in Velocidex Velociraptor below version 0.76.5 allows any authenticated low-privilege user to retrieve the complete ACL policy (roles and permissions) for any user across all organizations by supplying targeted Name and Org parameters via a network request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7573
- https://docs.velociraptor.app/announcements/advisories/cve-2026-7573
- https://github.com/Velocidex/velociraptor
