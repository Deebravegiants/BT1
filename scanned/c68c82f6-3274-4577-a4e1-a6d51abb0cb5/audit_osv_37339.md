# [C] CVE-2026-31242

## Summary
Severity: Critical
Advisory: CVE-2026-31242
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-31242
Type: osv

## Details
The mem0 v1.0.0 server lacks authentication and authorization controls for its memory reset functionality accessible via the DELETE /memories endpoint. An unauthenticated attacker can send a DELETE request that triggers a reset operation, leading to the execution of a DROP TABLE SQL statement. This results in the deletion of the entire memory database table, causing catastrophic data loss and a complete denial of service for all users of the service.

## References
- https://www.notion.so/CVE-2026-31242-35d1e1393188819c9ebec0e684b4e656
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31242.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31242
- https://github.com/mem0ai/mem0
