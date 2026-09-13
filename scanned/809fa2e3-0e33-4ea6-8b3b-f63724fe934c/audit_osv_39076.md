# [M] HestiaCP 1.2.0-1.9.4 IP Spoofing via CF-Connecting-IP Header

## Summary
Severity: Medium
Advisory: CVE-2026-43634
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-43634
Type: osv

## Details
HestiaCP versions 1.2.0 through 1.9.4 contain an IP spoofing vulnerability that allows unauthenticated remote attackers to bypass authentication security controls by supplying an arbitrary IP address in the CF-Connecting-IP HTTP header without verifying the request originated from Cloudflare's network. Attackers can exploit this to circumvent fail2ban brute-force protection, bypass per-user IP allowlists, and poison authentication audit logs by spoofing trusted IP addresses on each request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43634.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43634
- https://www.vulncheck.com/advisories/hestiacp-ip-spoofing-via-cf-connecting-ip-header
- https://github.com/hestiacp/hestiacp/issues/5229
- https://github.com/hestiacp/hestiacp/pull/5273
- https://github.com/hestiacp/hestiacp/commit/f381e294500f671cf12716c638afd0bfde901f88
- https://github.com/hestiacp/hestiacp
- https://mercuryiss.com.au/hestiacp-unauthenticated-rce-ip-spoofing-cve-2026-43633-cve-2026-43634
