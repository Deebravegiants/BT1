# [C] Sim Studio AI - MongoDB SSRF and Arbitrary Document Deletion

## Summary
Severity: Critical
Advisory: CVE-2026-3431
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2026-3431
Type: osv

## Details
On SimStudio version below to 0.5.74, the MongoDB tool endpoints accept arbitrary connection parameters from the caller without authentication or host restrictions. An attacker can leverage these endpoints to connect to any reachable MongoDB instance and perform unauthorized operations including reading, modifying, and deleting data.

## References
- https://www.tenable.com/security/research/tra-2026-12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3431.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3431
- https://github.com/simstudioai/sim
