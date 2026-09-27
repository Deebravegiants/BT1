# [M] Stunnel: ssrf bypass in stunnel socks proxy via ipv4-mapped ipv6 loopback and unspecified addresses allows access to loopback-only services

## Summary
Severity: Medium
Advisory: CVE-2026-70367
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-70367
Type: osv

## Details
A Server-Side Request Forgery (SSRF) bypass vulnerability exists in “stunnel” 5.79 and lower when configured in SOCKS proxy mode. This flaw allows a client to bypass intended localhost restrictions by using IPv4-mapped IPv6 addresses (e.g., “::ffff:127.0.0.1”) or unspecified addresses ("0.0.0.0", "::"), enabling access to loopback-only services on the "stunnel" host that should not be network-reachable.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-70367
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70367.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70367
- https://bugzilla.redhat.com/show_bug.cgi?id=2462083
- https://github.com/mtrojnar/stunnel
