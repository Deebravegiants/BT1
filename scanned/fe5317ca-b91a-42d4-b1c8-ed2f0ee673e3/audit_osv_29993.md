# [H] CVE-2024-48651

## Summary
Severity: High
Advisory: CVE-2024-48651
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-48651
Type: osv

## Details
In ProFTPD through 1.3.8b before cec01cc, supplemental group inheritance grants unintended access to GID 0 because of the lack of supplemental groups from mod_sql.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00032.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48651.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48651
- https://github.com/proftpd/proftpd/issues/1830
- https://github.com/proftpd/proftpd/commit/cec01cc0a2523453e5da5a486bc6d977c3768db1
