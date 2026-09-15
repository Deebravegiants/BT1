# [M] Roxy-WI: SSRF in /smon/agent/<endpoint>/<server_ip> reachable to cloud metadata IPs

## Summary
Severity: Medium
Advisory: CVE-2026-45561
Aliases: GHSA-2crj-7rqc-x7rq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45561
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, the /smon/agent/{version,uptime,status,checks}/<server_ip> family of routes takes the URL path component verbatim into requests.get(f'http://{server_ip}:{agent_port}/...'). The path component is constrained only by Flask's default URL converter, which permits any value (including IPv4 literals like 169.254.169.254, RFC1918 ranges, and 127.0.0.1). At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45561.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-2crj-7rqc-x7rq
- https://nvd.nist.gov/vuln/detail/CVE-2026-45561
