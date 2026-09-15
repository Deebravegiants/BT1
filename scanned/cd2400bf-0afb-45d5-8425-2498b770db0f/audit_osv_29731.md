# [H] CVE-2024-45846

## Summary
Severity: High
Advisory: CVE-2024-45846
Aliases: GHSA-wcjw-3v6p-4v3r, PYSEC-2024-77
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-12
Source: https://osv.dev/vulnerability/CVE-2024-45846
Type: osv

## Details
An arbitrary code execution vulnerability exists in versions 23.10.3.0 up to 24.7.4.1 of the MindsDB platform, when the Weaviate integration is installed on the server. If a specially crafted ‘SELECT WHERE’ clause containing Python code is run against a database created with the Weaviate engine, the code will be passed to an eval function and executed on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45846.json
- https://hiddenlayer.com/sai-security-advisory/2024-09-mindsdb/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45846
- https://github.com/mindsdb/mindsdb
