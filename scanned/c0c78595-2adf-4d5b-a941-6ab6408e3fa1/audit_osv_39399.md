# [C] Roxy-WI: IDOR on PUT /smon/check — any user can rewrite any tenant's monitoring URL/IP/body

## Summary
Severity: Critical
Advisory: CVE-2026-45550
Aliases: GHSA-856h-mvm2-2h2x
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45550
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, PUT /smon/check (app/routes/smon/routes.py:117-138) gates only on roxywi_common.check_user_group_for_flask() — which validates that the caller has some group, not that the target check_id belongs to it. The downstream SQL update functions update_smon, update_smonHttp, update_smonTcp, update_smonPing, update_smonDns (app/modules/db/smon.py:515-562) all execute WHERE smon_id = ? with no user_group filter. The DELETE path is correctly filtered (app/modules/db/smon.py:319-327 does WHERE id = ? AND user_group = ?), demonstrating that the maintainers know the right pattern but did not apply it on UPDATE. Therefore any authenticated user can iterate over smon_id values and silently rewrite any other tenant's HTTP / TCP / Ping / DNS monitoring check. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45550.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-856h-mvm2-2h2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-45550
