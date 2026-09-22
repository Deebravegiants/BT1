# [M] File Browser has an Authorization Policy Bypass in Public Share Download Flow

## Summary
Severity: Medium
Advisory: GHSA-68j5-4m99-w9w9
CVE: CVE-2026-32761
CWE: CWE-284, CWE-639, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-68j5-4m99-w9w9
Type: github-advisory

## Affected
- Go: `https://github.com/filebrowser/filebrowser` — affected >=0

## Details
### Summary
A permission enforcement flaw allows users without download privileges (`download=false`) to still expose and retrieve file content via public share links when they retain share privileges (`share=true`). This bypasses intended access control policy and enables unauthorized data exfiltration to unauthenticated users. Where download restrictions are used for data-loss prevention or role separation.

### Details
The backend applies inconsistent authorization checks across download paths:

- Direct raw download correctly enforces `Perm.Download`:
  - [[raw.go](https://github.com/filebrowser/filebrowser/blob/master/http/raw.go#82)](filebrowser/http/raw.go:82)
- Share creation only enforces `Perm.Share`:
  - [[share.go](https://github.com/filebrowser/filebrowser/blob/master/http/share.go#21)](filebrowser/http/share.go:21)
- Public share/download handlers serve shared content without verifying owner `Perm.Download`:
  - [public.go](https://github.com/filebrowser/filebrowser/blob/master/http/public.go#18)(filebrowser/http/public.go:18)
  - [public.go](https://github.com/filebrowser/filebrowser/blob/master/http/public.go#116)(filebrowser/http/public.go:116)

As a result, a user who is blocked from direct downloads can create a share and obtain the same file via `/api/public/dl/<hash>`.

### PoC

1. Create a non-admin user with:
- `perm.share = true`
- `perm.download = false`

2. Login as that user and upload a **PDF** file:
- `POST /api/resources/nodl_secret_<rand>.pdf` with `Content-Type: application/pdf`

3. Verify direct raw download is denied:
- `GET /api/raw/nodl_secret_<rand>.pdf`
- Expected and observed: `202 Accepted` (blocked)

4. Create share for same file:
- `POST /api/share/nodl_secret_<rand>.pdf`
- Observed: `200`, response includes `hash` (example: `qxfK3JMG`)

5. Download publicly without authentication:
- `GET /api/public/dl/<hash>`
- Observed (vulnerable): `200`, `Content-Type: application/pdf`, and PDF bytes are returned

Live evidence captured (March 1, 2026):
- `create user`: `201`
- `create file`: `200`
- `direct /api/raw`: `202 Accepted`
- `create share`: `200`
- `public download /api/public/dl/mxK-ppZb`: `200`
- `public download content-type`: `application/pdf`
- `public download body length`: `327` bytes

### Impact
This is an **access control / authorization policy bypass** vulnerability.

- **Who can exploit:** Any authenticated user granted `share=true` but denied `download`.
- **Who is impacted:** Operators and organizations relying on download restrictions to prevent data export.
- **What can happen:** Restricted users can still distribute and retrieve files publicly, including unauthenticated access through share URLs.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-68j5-4m99-w9w9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32761
- https://github.com/filebrowser/filebrowser/commit/09a26166b4f79446e7174c017380f6db45444e32
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.62.0
