# [C] Roxy-WI: Authenticated RCE on every managed HAProxy load balancer via `option` field config injection in section save

## Summary
Severity: Critical
Advisory: CVE-2026-45558
Aliases: GHSA-w2x4-66jj-3597
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45558
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, the HAProxy section-save endpoints (POST /api/service/haproxy/<server_id>/section/<section_type> and the PUT / global / defaults variants) accept a JSON option field that is not validated, not escaped, and is rendered verbatim into the generated HAProxy configuration via the section.j2, global.j2, and defaults.j2 Ansible templates. Because Roxy-WI then pushes the generated config to the load balancer and runs systemctl reload haproxy, an authenticated user with role ≤ 3 (user) can inject arbitrary HAProxy directives into the config that runs on every load balancer their group manages — including option external-check + external-check command /bin/bash -c '…', which gives remote code execution on the load balancer as the haproxy user on every health-check tick. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45558.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-w2x4-66jj-3597
- https://nvd.nist.gov/vuln/detail/CVE-2026-45558
