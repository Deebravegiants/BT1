# [M] CVE-2026-31243

## Summary
Severity: Medium
Advisory: CVE-2026-31243
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-31243
Type: osv

## Details
The mem0 1.0.0 server lacks authentication and authorization controls for its memory reset and table re-creation functionality accessible via the DELETE /memories endpoint. An unauthenticated attacker can send a DELETE request that triggers a reset operation, leading to the execution of a CREATE TABLE SQL statement. This can cause unexpected table re-creation, schema disruption, potential data loss, and denial of service for the memory management service.

## References
- https://www.notion.so/CVE-2026-31243-35d1e139318881c6a6cffbe366c238a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31243.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31243
- https://github.com/mem0ai/mem0
