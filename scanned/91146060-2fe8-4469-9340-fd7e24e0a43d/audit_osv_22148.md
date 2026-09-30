# [H] NocoDB - CSV Injection in User Management

## Summary
Severity: High
Advisory: CVE-2022-22121
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2022-22121
Type: osv

## Details
In NocoDB, versions 0.81.0 through 0.83.8 are affected by CSV Injection vulnerability (Formula Injection). A low privileged attacker can create a new table to inject payloads in the table rows. When an administrator accesses the User Management endpoint and exports the data as a CSV file and opens it, the payload gets executed.

## References
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-22121
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/22xxx/CVE-2022-22121.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-22121
- https://github.com/nocodb/nocodb/commit/079e3abe
