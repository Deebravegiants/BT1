# [H] Roxy-WI: Authorization bypass on POST /smon/agent/action/<action> — guest can stop or restart smon-agent on any host

## Summary
Severity: High
Advisory: CVE-2026-45549
Aliases: GHSA-c92j-h72m-ff4j
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45549
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, agent_action (app/routes/smon/agent_routes.py:166-179) has decorators @bp.post('/agent/action/<action>') and @jwt_required() only — no role check, no group ownership check on the server_ip form field. Any authenticated user, including role 4 (guest), can start, stop, or restart the roxy-wi-smon-agent systemd unit on any server they can name. Roxy-WI executes the systemd action over its own SSH credentials (passwordless sudo), so the action runs as root on the target. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45549.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-c92j-h72m-ff4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-45549
