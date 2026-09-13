# [C] pgAdmin 4: Remote Code Execution in Query Tool and Cloud Deployment

## Summary
Severity: Critical
Advisory: CVE-2025-2945
Aliases: GHSA-g73c-fw68-pwx3, PYSEC-2026-451
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-2945
Type: osv

## Details
Remote Code Execution security vulnerability in pgAdmin 4  (Query Tool and Cloud Deployment modules).

The vulnerability is associated with the 2 POST endpoints; /sqleditor/query_tool/download, where the query_commited parameter and /cloud/deploy endpoint, where the high_availability parameter is unsafely passed to the Python eval() function, allowing arbitrary code execution.


This issue affects pgAdmin 4: before 9.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2945.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2945
- https://github.com/pgadmin-org/pgadmin4/issues/8603
- https://github.com/pgadmin-org/pgadmin4
