# [M] CVE-2026-31245

## Summary
Severity: Medium
Advisory: CVE-2026-31245
Aliases: GHSA-cgx8-qgvr-f7vf, PYSEC-2026-2633
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-31245
Type: osv

## Details
The mem0 1.0.0 server lacks authentication and authorization controls for its memory creation API endpoint (POST /memories). The endpoint allows unauthenticated users to submit arbitrary memory records without verifying their identity or permissions. A remote attacker can exploit this by sending unauthenticated POST requests to create malicious or spoofed memory entries in the database, leading to unauthorized data injection and potential data pollution.

## References
- https://www.notion.so/CVE-2026-31245-35d1e1393188810aab57ff9b49146b05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31245.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31245
- https://github.com/mem0ai/mem0
