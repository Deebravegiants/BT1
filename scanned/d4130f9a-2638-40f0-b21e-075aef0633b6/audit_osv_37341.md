# [M] CVE-2026-31244

## Summary
Severity: Medium
Advisory: CVE-2026-31244
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-31244
Type: osv

## Details
The mem0 1.0.0 server lacks authentication and authorization controls for its memory deletion API endpoint (DELETE /memories/{memory_id}). The endpoint allows unauthenticated users to delete arbitrary memory records without verifying their identity or permissions. A remote attacker can exploit this by sending unauthenticated DELETE requests to remove any memory entry from the database, leading to unauthorized data loss and potential denial of service.

## References
- https://www.notion.so/CVE-2026-31244-35d1e1393188818b8039c50adc75996c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31244.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31244
- https://github.com/mem0ai/mem0
