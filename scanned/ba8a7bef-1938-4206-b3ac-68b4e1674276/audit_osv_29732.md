# [H] CVE-2024-45847

## Summary
Severity: High
Advisory: CVE-2024-45847
Aliases: GHSA-crmg-rp64-5cm3, PYSEC-2026-1629
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-12
Source: https://osv.dev/vulnerability/CVE-2024-45847
Type: osv

## Details
An arbitrary code execution vulnerability exists in versions 23.11.4.2 up to 24.7.4.1 of the MindsDB platform, when one of several integrations is installed on the server. If a specially crafted ‘UPDATE’ query containing Python code is run against a database created with the specified integration engine, the code will be passed to an eval function and executed on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45847.json
- https://hiddenlayer.com/sai-security-advisory/2024-09-mindsdb/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45847
- https://github.com/mindsdb/mindsdb
