# [C] CVE-2025-22992

## Summary
Severity: Critical
Advisory: CVE-2025-22992
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-06
Source: https://osv.dev/vulnerability/CVE-2025-22992
Type: osv

## Details
A SQL Injection vulnerability exists in the /feed/insert.json endpoint of the Emoncms project >= 11.6.9. The vulnerability is caused by improper handling of user-supplied input in the data query parameter, allowing attackers to execute arbitrary SQL commands under specific conditions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22992.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22992
- https://github.com/emoncms/emoncms/issues/1916
