# [H] CVE-2026-44331

## Summary
Severity: High
Advisory: CVE-2026-44331
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-44331
Type: osv

## Details
In ProFTPD through 1.3.9a before 7666224, a SQL injection vulnerability in sqltab_fetch_clients_cb() in contrib/mod_wrap2_sql.c allows a remote attacker to inject arbitrary SQL commands via a crafted domain name that is accessed in a reverse DNS lookup. When "UseReverseDNS on" is enabled, the attacker-supplied hostname is passed unescaped into SQL queries. The character restrictions of DNS names may affect exploitability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44331.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-44331
- https://github.com/proftpd/proftpd/issues/2057
- https://github.com/proftpd/proftpd/commit/766622456440fbca33abd7927c523673a11d1ed1
