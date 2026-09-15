# [C] DB User Password Leak in Application Log

## Summary
Severity: Critical
Advisory: CVE-2024-0006
CVSS: 9.0 (CVSS:4.0/AV:A/AC:H/AT:N/PR:H/UI:A/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2024-07-19
Source: https://osv.dev/vulnerability/CVE-2024-0006
Type: osv

## Details
Information exposure in the logging system in Yugabyte Platform allows local attackers with access to application logs to obtain database user credentials in log files, potentially leading to unauthorized database access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0006.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0006
- https://github.com/yugabyte/yugabyte-db/commit/439c6286f1971f9ac6bff2c7215b454c2025c593
- https://github.com/yugabyte/yugabyte-db/commit/5cc7f4e15d6ccccbf97c57946fd0aa630f88c9e2
- https://github.com/yugabyte/yugabyte-db/commit/d96e6b629f34d065b47204daeeb44064e484c579
