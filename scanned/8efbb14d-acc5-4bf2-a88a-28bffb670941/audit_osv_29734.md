# [H] CVE-2024-45849

## Summary
Severity: High
Advisory: CVE-2024-45849
Aliases: GHSA-c85f-pcx6-2ghm, PYSEC-2024-79
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-12
Source: https://osv.dev/vulnerability/CVE-2024-45849
Type: osv

## Details
An arbitrary code execution vulnerability exists in versions 23.10.5.0 up to 24.7.4.1 of the MindsDB platform, when the Microsoft SharePoint integration is installed on the server. For databases created with the SharePoint engine, an ‘INSERT’ query can be used for list creation. If such a query is specially crafted to contain Python code and is run against the database, the code will be passed to an eval function and executed on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45849.json
- https://hiddenlayer.com/sai-security-advisory/2024-09-mindsdb/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45849
- https://github.com/mindsdb/mindsdb
