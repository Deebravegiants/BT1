# [C] Roxy-WI: Cross-tenant authorization bypass on /install/* — guest can run Ansible / SSH on every registered server

## Summary
Severity: Critical
Advisory: CVE-2026-45552
Aliases: GHSA-v3f8-g2v8-jq5h
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45552
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, the install blueprint declares only bp.before_request → @jwt_required() (app/routes/install/routes.py:36-39). The individual endpoints install_exporter, install_waf, install_geoip, check_geoip, get_exporter_version, and get_task_status are not wrapped in page_for_admin and do not call roxywi_common.is_user_has_access_to_its_group(server_ip) or check_is_server_in_group(server_ip). Only the GET index page (install_monitoring) gates on roxywi_auth.page_for_admin(level=2). Because the missing decorators omit both role and group checks, any logged-in user — including the default guest role 4 — can install/reconfigure exporters, WAF, and GeoIP databases on every server in the Roxy-WI database, regardless of tenant ownership. The Ansible playbooks run with the per-server SSH credential stored in Roxy-WI, which the credentials' rightful owner (a different tenant) has provisioned with sudo rights for the management workflow. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45552.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-v3f8-g2v8-jq5h
- https://nvd.nist.gov/vuln/detail/CVE-2026-45552
