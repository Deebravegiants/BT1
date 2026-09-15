# [H] SQL Injection on Jorani

## Summary
Severity: High
Advisory: CVE-2023-2681
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-03
Source: https://osv.dev/vulnerability/CVE-2023-2681
Type: osv

## Details
An SQL Injection vulnerability has been found on Jorani version 1.0.0. This vulnerability allows an authenticated remote user, with low privileges, to send queries with malicious SQL code on the "/leaves/validate" path and the “id” parameter, managing to extract arbritary information from the database.

## References
- https://www.incibe.es/en/incibe-cert/notices/aviso/jorani-sql-injection
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2681.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2681
