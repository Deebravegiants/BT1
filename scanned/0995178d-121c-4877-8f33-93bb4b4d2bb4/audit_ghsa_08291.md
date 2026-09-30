# [H] mem0 server lacks authentication and authorization controls for its memory management API endpoints

## Summary
Severity: High
Advisory: GHSA-jfv9-68m5-gjjr
CVE: CVE-2026-31240
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-jfv9-68m5-gjjr
Type: github-advisory

## Affected
- PyPI: `mem0ai` — affected >=0

## Details
The mem0 1.0.0 server lacks authentication and authorization controls for its memory management API endpoints. Critical functions such as updating memory records (PUT /memories/{memory_id}) are exposed without any verification of the requester's identity or permissions. A remote attacker can exploit this by sending unauthenticated requests to modify, overwrite, or delete arbitrary memory records, leading to unauthorized data manipulation and potential data loss.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31240
- https://github.com/mem0ai/mem0
- https://www.notion.so/CVE-2026-31240-35d1e13931888170964ae035c04a8f18
