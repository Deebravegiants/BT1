# [C] Unauthenticated arbitrary file read via /uploads path traversal (URL-encoded separators) leading to instance takeover

## Summary
Severity: Critical
Advisory: CVE-2026-19264
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-19264
Type: osv

## Details
Postiz is an open-source social media scheduling tool. The route that serves locally stored media joins URL-supplied path segments onto the upload directory and streams the file without normalising the path or confining it to that directory, and the route requires no authentication. Raw dot-segments are collapsed before routing, but URL-encoded separators survive route matching and are decoded only once they reach the handler, restoring the traversal at the filesystem call. An unauthenticated remote attacker can therefore read any file readable by the application process, including the process environment, which exposes the JWT signing secret, the database connection string, and connected provider and billing secrets. Because session tokens are signed with that secret and carry no expiry, this allows forging a non-expiring session as any user, including an administrator, without a password.

## References
- https://gadvisory.org/advisories/PSA-2026-TH12B7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19264.json
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.22.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-19264
- https://github.com/gitroomhq/postiz-app/commit/7936062
- https://github.com/gitroomhq/postiz-app
