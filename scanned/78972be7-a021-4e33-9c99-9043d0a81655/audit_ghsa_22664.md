# [C] Rancher Recreates Default User With Known Password Despite Deletion

## Summary
Severity: Critical
Advisory: GHSA-xh8x-j8h3-m5ph
CVE: CVE-2019-11202
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xh8x-j8h3-m5ph
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.0.0
- Go: `github.com/rancher/rancher` — affected >=2.1.0
- Go: `github.com/rancher/rancher` — affected >=2.2.0 <2.2.2

## Details
An issue was discovered that affects the following versions of Rancher: v2.0.0 through v2.0.13, v2.1.0 through v2.1.8, and v2.2.0 through 2.2.1. When Rancher starts for the first time, it creates a default admin user with a well-known password. After initial setup, the Rancher administrator may choose to delete this default admin user. If Rancher is restarted, the default admin user will be recreated with the well-known default password. An attacker could exploit this by logging in with the default admin credentials. This can be mitigated by deactivating the default admin user rather than completing deleting them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11202
- https://forums.rancher.com/t/rancher-release-v2-2-2-addresses-rancher-cve-2019-11202-and-stability-issues/13977
- https://github.com/advisories/GHSA-xh8x-j8h3-m5ph
- https://github.com/rancher/rancher
- https://pkg.go.dev/vuln/GO-2024-2784
