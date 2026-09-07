# [H] Vanna vulnerable to SQL Injection

## Summary
Severity: High
Advisory: GHSA-mwxm-35f8-6vg2
CVE: CVE-2024-5753
CWE: CWE-200, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-mwxm-35f8-6vg2
Type: github-advisory

## Affected
- PyPI: `vanna` — affected >=0

## Details
vanna-ai/vanna version v0.3.4 is vulnerable to SQL injection in some file-critical functions such as `pg_read_file()`. This vulnerability allows unauthenticated remote users to read arbitrary local files on the victim server, including sensitive files like `/etc/passwd`, by exploiting the exposed SQL queries via a Python Flask API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5753
- https://github.com/vanna-ai/vanna
- https://huntr.com/bounties/a3f913d6-c717-4528-b974-26d8d9e839ca
