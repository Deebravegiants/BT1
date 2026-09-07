# [M] Mattermost doesn't sanitize the Remote Cluster API response on PATCH operations

## Summary
Severity: Medium
Advisory: GHSA-9p44-r552-4wp9
CVE: CVE-2026-7184
CWE: CWE-201
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-9p44-r552-4wp9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.16
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20250731163400-5b955468ea1e <8.0.0-20260428142921-bd8fc9222672

## Details
Mattermost versions 11.6.x <= 11.6.1, 11.5.x <= 11.5.4, 10.11.x <= 10.11.15 fail to sanitize the Remote Cluster API response on PATCH operations, which allows authenticated users with the {{manage_secure_connections}} permission to obtain remote cluster authentication tokens via a PATCH request to the remote cluster endpoint. Mattermost Advisory ID: MMSA-2026-00662

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7184
- https://github.com/mattermost/mattermost/pull/36313
- https://github.com/mattermost/mattermost/pull/36311
- https://github.com/mattermost/mattermost/pull/36310
- https://github.com/mattermost/mattermost/pull/36306
- https://github.com/mattermost/mattermost/pull/36288
- https://github.com/mattermost/mattermost/commit/cad3e8e51a4d8627af6442f9df8ae3667fac7fc1
- https://github.com/mattermost/mattermost/commit/c5e67e28271c23cb585fe1a30ae81defcde848d6
- https://github.com/mattermost/mattermost/commit/bd8fc92226726da06c8fabaef568cc9ebaee1cb8
- https://github.com/mattermost/mattermost/commit/6fd49f56b5920569218fd2fc76d8ae802942f274
- https://github.com/mattermost/mattermost/commit/1a0643df00c1f51a3b7e919eec034eaf955f612f
- https://github.com/mattermost/mattermost/releases/tag/v10.11.16
- https://github.com/mattermost/mattermost/releases/tag/v11.5.5
- https://github.com/mattermost/mattermost/releases/tag/v11.6.2
- https://github.com/mattermost/mattermost/releases/tag/v11.7.0
- https://mattermost.com/security-updates
- https://github.com/mattermost/mattermost
