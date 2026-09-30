# [M] CVE-2026-82477

## Summary
Severity: Medium
Advisory: CVE-2026-82477
Aliases: GHSA-g9vx-2rpf-gpch
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82477
Type: osv

## Details
In MITRE SAF Heimdall 2.11.6 through 2.13.x before 2.14.0, an SSRF issue allows remote attackers to access internal network resources via the Tenable proxy endpoint. This occurs in apps/backend/src/tenable/tenable.controller.ts.

## References
- https://github.com/mitre/heimdall2/releases/tag/v2.14.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82477.json
- https://github.com/mitre/heimdall2/security/advisories/GHSA-g9vx-2rpf-gpch
- https://nvd.nist.gov/vuln/detail/CVE-2026-82477
- https://github.com/mitre/heimdall2/commit/b6a9cdb4fc01f96aaa1a77cc27d1d449b485937b
