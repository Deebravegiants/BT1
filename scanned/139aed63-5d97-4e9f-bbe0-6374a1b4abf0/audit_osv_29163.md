# [H] Vertex Vulnerable to Path Traversal

## Summary
Severity: High
Advisory: CVE-2024-40646
Aliases: GHSA-92j5-qc36-23rr
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2024-40646
Type: osv

## Details
Vertex is a management tool for PT (Private Tracker) users to manage streaming and watching videos. Versions prior to commit fbde301b97986d5913fc4bc95f5445750d282e11 are vulnerable to path traversal. Users should upgrade to a version containing commit fbde301b97986d5913fc4bc95f5445750d282e11 to receive a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40646.json
- https://github.com/vertex-app/vertex/security/advisories/GHSA-92j5-qc36-23rr
- https://nvd.nist.gov/vuln/detail/CVE-2024-40646
- https://github.com/vertex-app/vertex/commit/fbde301b97986d5913fc4bc95f5445750d282e11
