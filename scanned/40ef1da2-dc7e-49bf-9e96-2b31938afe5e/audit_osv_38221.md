# [M] Bulwark Webmail getClientIP() trusted client-controlled X-Forwarded-For value, enabling rate limit bypass and audit log forgery

## Summary
Severity: Medium
Advisory: CVE-2026-35391
Aliases: GHSA-7pj2-232x-6698
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35391
Type: osv

## Details
Bulwark Webmail is a self-hosted webmail client for Stalwart Mail Server. Prior to 1.4.11, the getClientIP() function in lib/admin/session.ts trusted the first (leftmost) entry of the X-Forwarded-For header, which is fully controlled by the client. An attacker could forge their source IP address to bypass IP-based rate limiting (enabling brute-force attacks against the admin login) or forge audit log entries (making malicious activity appear to originate from arbitrary IP addresses). This vulnerability is fixed in 1.4.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35391.json
- https://github.com/bulwarkmail/webmail/security/advisories/GHSA-7pj2-232x-6698
- https://nvd.nist.gov/vuln/detail/CVE-2026-35391
