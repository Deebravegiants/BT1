# [M] Roxy-WI: LDAP injection in /user/ldap/<username> (admin-only)

## Summary
Severity: Medium
Advisory: CVE-2026-45559
Aliases: GHSA-2257-7mhp-grqp
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45559
Type: osv

## Details
Roxy-WI is a web interface for managing Haproxy, Nginx, Apache and Keepalived servers. In versions 8.2.6.4 and prior, get_ldap_email (app/modules/roxywi/user.py:120-157) builds the LDAP search filter via f-string concatenation. The username URL path parameter is taken verbatim — no checkAjaxInput, no LDAP escape — and inserted, a username like *)(mail=*)(cn=* injects additional clauses, allowing the admin to enumerate or harvest attributes outside the intended record. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45559.json
- https://github.com/roxy-wi/roxy-wi/security/advisories/GHSA-2257-7mhp-grqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45559
