# [M] Prisma Injection in mintplex-labs/anything-llm

## Summary
Severity: Medium
Advisory: CVE-2024-8251
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-8251
Type: osv

## Details
A vulnerability in mintplex-labs/anything-llm prior to version 1.2.2 allows for Prisma injection. The issue exists in the API endpoint "/embed/:embedId/stream-chat" where user-provided JSON is directly taken to the Prisma library's where clause. An attacker can exploit this by providing a specially crafted JSON object, such as {"sessionId":{"not":"a"}}, causing Prisma to return all data from the table. This can lead to unauthorized access to all user queries in embedded chat mode.

## References
- https://huntr.com/bounties/7c263ef1-7d50-475a-9425-b15df4e0403c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8251.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8251
- https://github.com/mintplex-labs/anything-llm/commit/334fd9cdd02ad4aa6a3c9bdfc95e7764651c13f4
