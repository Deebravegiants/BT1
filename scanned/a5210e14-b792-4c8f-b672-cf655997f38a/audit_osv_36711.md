# [C] CVE-2026-25212

## Summary
Severity: Critical
Advisory: CVE-2026-25212
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-25212
Type: osv

## Details
An issue was discovered in Percona PMM before 3.7. Because an internal database user retains specific superuser privileges, an attacker with pmm-admin rights can abuse the "Add data source" feature to break out of the database context and execute shell commands on the underlying operating system.

## References
- https://docs.percona.com/percona-monitoring-and-management/3/release-notes/3.7.0.html#authenticated-remote-code-execution-via-internal-data-source-cve-2026-25212
- https://percona.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25212.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25212
