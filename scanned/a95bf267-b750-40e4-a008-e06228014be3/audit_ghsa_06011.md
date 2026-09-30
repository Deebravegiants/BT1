# [M] rclone: WebDAV Credentials Survive a Same-Host HTTPS-to-HTTP Redirect

## Summary
Severity: Medium
Advisory: GHSA-h4mf-4v27-hggj
CWE: CWE-319, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-h4mf-4v27-hggj
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=0 <1.75.0

## Details
## 1. Summary

WebDAV's default redirect handling can replay Basic authorization and configured Cookie headers over plaintext HTTP after a same-host HTTPS-to-HTTP redirect. This was reproduced through the real backend. Unlike the low-impact STS token in rclone's published S3 redirect advisory, Basic passwords and session cookies are complete reusable credentials, supporting a High rating when they grant normal WebDAV read/write access.

The credible threat requires a legitimate endpoint, gateway, or accelerator to emit an unsafe redirect and an adjacent/on-path actor to observe the plaintext hop. A report should not rely on a malicious original WebDAV endpoint because that endpoint already receives the credentials.

## 2. Affected Assets & Attack Surface

- Backend configuration/authentication: `backend/webdav/webdav.go:127-139`, `170-206`, `440-530`
- Shared redirect callback: `lib/rest/rest.go:218-231`
- HTTP client: `fs/fshttp/http.go:311-329`
- Credentials: Basic passwords, bearer authorization, SharePoint/session cookies, and configured secret headers
- Confirmed affected version: `<= v1.74.0-240`

## 3. Technical Root Cause Analysis

`PreserveMethodRedirectFn` limits redirect count and restores the original method, but it does not reject a transport downgrade or compare the full origin tuple. The client therefore relies on Go's hostname-oriented sensitive-header forwarding rules. Those rules can preserve `Authorization` and Cookie on a same-host redirect even when the new scheme is plaintext HTTP.

## 4. Proof-of-Concept & Evidence

1. Configure the actual WebDAV backend with Basic credentials and a Cookie.
2. Have the TLS endpoint return `307 Temporary Redirect` to an HTTP listener on the same hostname and a different port.
3. rclone follows the redirect while preserving the WebDAV method.
4. The plaintext listener receives both the Basic `Authorization` value and Cookie.

## 5. Impact Assessment

An on-path observer can reuse the captured password, bearer token, or session cookie for the account's permitted WebDAV operations. Confidentiality, integrity, and availability impact depend on that account's permissions.

## 6. Remediation Guidance

- Reject every HTTPS-to-HTTP redirect before replay.
- Forward authenticated requests by default only when scheme, hostname, and effective port are unchanged.
- Strip authorization, cookies, proxy credentials, and configured secret headers on all other redirects.
- Put necessary provider exceptions behind exact destination allowlists.
- Cover `301`, `302`, `303`, `307`, and `308` in regression tests.

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-h4mf-4v27-hggj
- https://github.com/rclone/rclone/commit/59b513b0e74fd2943ccbb8891d5ce00f860e6d26
- https://github.com/rclone/rclone
- https://github.com/rclone/rclone/releases/tag/v1.75.0
