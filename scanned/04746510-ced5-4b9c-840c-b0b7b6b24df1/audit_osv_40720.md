# [H] Frigate viewer can read logs exposing admin and camera credentials

## Summary
Severity: High
Advisory: CVE-2026-54652
Aliases: GHSA-c4qf-xxq4-vf55
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-54652
Type: osv

## Details
Frigate is an open source network video recorder. In version 0.17.1, the GET /api/logs/{service} endpoint allows any authenticated user including the viewer role to download Frigate and nginx logs, exposing auto-generated admin passwords and camera credentials logged in request query strings and enabling viewer-to-admin privilege escalation. A fixed release has not been identified.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54652.json
- https://github.com/blakeblackshear/frigate/security/advisories/GHSA-c4qf-xxq4-vf55
- https://nvd.nist.gov/vuln/detail/CVE-2026-54652
- https://github.com/blakeblackshear/frigate/commit/68e8afd35c76f05f68de47ee9588d2c91796de4b
- https://github.com/blakeblackshear/frigate/commit/bd1fc1cc72cd4fa371464a087cbf3d7f3142edc6
