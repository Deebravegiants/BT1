# [H] SQL injection in syslog-ng SQL destionation driver

## Summary
Severity: High
Advisory: CVE-2026-39879
Aliases: GHSA-qwf9-6222-m24m
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-39879
Type: osv

## Details
Due to a missing sanitization call in [`afsql_dd_run_query`](https://github.com/syslog-ng/syslog-ng/blob/649e6e18e3459fb4467000a88dfb12fa97f9719c/modules/afsql/afsql.c#L219), syslog-ng before 4.12 are vulnerable to SQL injection from an untrusted source. This is not part of the default configuration, the SQL driver has to be manually configured.

Fixes are in syslog-ng 4.12, syslog-ng Premium Edition 8.2 and syslog-ng Store Box 7.8

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39879.json
- https://github.com/syslog-ng/syslog-ng/security/advisories/GHSA-qwf9-6222-m24m
- https://nvd.nist.gov/vuln/detail/CVE-2026-39879
