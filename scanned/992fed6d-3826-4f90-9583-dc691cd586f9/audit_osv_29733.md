# [H] CVE-2024-45848

## Summary
Severity: High
Advisory: CVE-2024-45848
Aliases: GHSA-9gq6-6936-885w, PYSEC-2024-78
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-12
Source: https://osv.dev/vulnerability/CVE-2024-45848
Type: osv

## Details
An arbitrary code execution vulnerability exists in versions 23.12.4.0 up to 24.7.4.1 of the MindsDB platform, when the ChromaDB integration is installed on the server. If a specially crafted ‘INSERT’ query containing Python code is run against a database created with the ChromaDB engine, the code will be passed to an eval function and executed on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45848.json
- https://hiddenlayer.com/sai-security-advisory/2024-09-mindsdb/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45848
- https://github.com/mindsdb/mindsdb
