# [H] Movary has Authenticated SSRF via Jellyfin Server URL Verification that Allows Internal Network Probing

## Summary
Severity: High
Advisory: CVE-2026-40348
Aliases: GHSA-2m2v-v563-qqvj
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-40348
Type: osv

## Details
Movary is a self hosted web app to track and rate a user's watched movies. Prior to version 0.71.1, an ordinary authenticated user can trigger server-side requests to arbitrary internal targets through `POST /settings/jellyfin/server-url-verify`. The endpoint accepts a user-controlled URL, appends `/system/info/public`, and sends a server-side HTTP request with Guzzle. Because there is no restriction on internal hosts, loopback addresses, or private network ranges, this can be abused for SSRF and internal network probing. Any ordinary authenticated user can use this endpoint to make the server connect to arbitrary internal targets and distinguish between different network states. This enables SSRF-based internal reconnaissance, including host discovery, port-state probing, and service fingerprinting. In certain deployments, it may also be usable to reach internal administrative services or cloud metadata endpoints that are not directly accessible from the outside. Version 0.71.1 fixes the issue.

## References
- https://github.com/leepeuker/movary/releases/tag/0.71.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40348.json
- https://github.com/leepeuker/movary/security/advisories/GHSA-2m2v-v563-qqvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-40348
- https://github.com/leepeuker/movary/commit/d459b3513293d41254f7093aef07010a8e5dcf04
- https://github.com/leepeuker/movary/pull/751
