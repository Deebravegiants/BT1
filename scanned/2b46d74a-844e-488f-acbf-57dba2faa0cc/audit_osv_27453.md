# [H] Remote code execution

## Summary
Severity: High
Advisory: CVE-2024-21649
Aliases: GHSA-w9h2-px87-74vx, PYSEC-2024-30
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-30
Source: https://osv.dev/vulnerability/CVE-2024-21649
Type: osv

## Details
The vantage6 technology enables to manage and deploy privacy enhancing technologies like Federated Learning (FL) and Multi-Party Computation (MPC). Prior to 4.2.0, authenticated users could inject code into algorithm environment variables, resulting in remote code execution.  This vulnerability is patched in 4.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21649.json
- https://github.com/vantage6/vantage6/security/advisories/GHSA-w9h2-px87-74vx
- https://nvd.nist.gov/vuln/detail/CVE-2024-21649
- https://github.com/vantage6/vantage6/commit/eac19db737145d3ca987adf037a454fae0790ddd
