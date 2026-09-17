# [M] Roxy-WI: IDOR — any authenticated user can read another user's full action history

## Summary
Severity: Medium
Advisory: CVE-2026-45563
Aliases: GHSA-wcmc-cjmw-54x9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45563
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, GET /history/<service>/<server_ip> re-uses the server_ip path parameter as a user-id when service == 'user', with no authorization check. Any authenticated user — even a guest in an unrelated group — can list any other user's full action audit trail (server IPs touched, configs deployed, services restarted). At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45563.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-wcmc-cjmw-54x9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45563
