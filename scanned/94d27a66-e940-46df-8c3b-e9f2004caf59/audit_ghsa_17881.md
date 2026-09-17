# [H] Harness Allows Arbitrary File Write in Gitness LFS server

## Summary
Severity: High
Advisory: GHSA-w469-hj2f-jpr5
CVE: CVE-2025-58158
CWE: CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-w469-hj2f-jpr5
Type: github-advisory

## Affected
- Go: `github.com/harness/gitness` — affected >=1.0.4 <3.3.0
- Go: `github.com/harness/gitness` — affected >=0 <1.0.4-gitspaces-beta.0.20250808064055-21c5ce42ae13

## Details
### Impact
Open Source Harness git LFS server (Gitness)  exposes api to retrieve and upload files via git LFS.  Implementation of upload git LFS file api is vulnerable to arbitrary file write.  Due to improper sanitization for upload path, a malicious authenticated user who has access to Harness Gitness server api can use a crafted upload request to write arbitrary file to any location on file system, may even compromise the server. 

Users using git LFS are vulnerable.

### Patches
Users have to upgrade to v3.3.0 . All previous versions are affected by this vulnerability.

## References
- https://github.com/harness/harness/security/advisories/GHSA-w469-hj2f-jpr5
- https://nvd.nist.gov/vuln/detail/CVE-2025-58158
- https://github.com/harness/harness/commit/21c5ce42ae13740b1cad47706c2ec85e72cc8c20
- https://github.com/harness/harness
