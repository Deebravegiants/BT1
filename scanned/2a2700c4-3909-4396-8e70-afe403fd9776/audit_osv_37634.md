# [H] Kan is Vulnerable to Unauthenticated SSRF via Attachment Download Endpoint

## Summary
Severity: High
Advisory: CVE-2026-32255
Aliases: GHSA-qrx8-9hc6-jvqg
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-32255
Type: osv

## Details
Kan is an open-source project management tool. In versions 0.5.4 and below, the /api/download/attatchment endpoint has no authentication and no URL validation. The Attachment Download endpoint accepts a user-supplied URL query parameter and passes it directly to fetch() server-side, and returns the full response body. An unauthenticated attacker can use this to make HTTP requests from the server to internal services, cloud metadata endpoints, or private network resources. This issue has been fixed in version 0.5.5. To workaround this issue, block or restrict access to /api/download/attatchment at the reverse proxy level (nginx, Cloudflare, etc.).

## References
- https://github.com/kanbn/kan/releases/tag/v0.5.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32255.json
- https://github.com/kanbn/kan/security/advisories/GHSA-qrx8-9hc6-jvqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32255
- https://github.com/kanbn/kan/commit/53397d8e81dc1494d94132848c1f0416f1152bd7
