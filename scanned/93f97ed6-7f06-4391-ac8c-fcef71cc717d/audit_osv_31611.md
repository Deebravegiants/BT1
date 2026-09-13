# [M] CDT before 1.4.5 Out-of-Bounds Read via opposedVertexInd

## Summary
Severity: Medium
Advisory: CVE-2025-15647
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2025-15647
Type: osv

## Details
CDT before 1.4.5 contains an out-of-bounds read vulnerability in the opposedVertexInd() function when constraint edge intersections are computed in floating point and round outside adjacent triangles. Attackers can supply nearly-degenerate constraint edges through geometry data to trigger an out-of-bounds array access that crashes the calling process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15647.json
- https://github.com/artem-ogre/CDT/releases/tag/1.4.5
- https://nvd.nist.gov/vuln/detail/CVE-2025-15647
- https://www.vulncheck.com/advisories/cdt-before-1.4.5-out-of-bounds-read-via-opposedvertexind
- https://github.com/artem-ogre/CDT/issues/212
- https://github.com/artem-ogre/CDT/commit/bf0d11ebfe3da0da72aed91816f665aef1b447cc
- https://github.com/artem-ogre/CDT
- https://github.com/artem-ogre/CDT/blob/1.4.4/CDT/include/CDTUtils.hpp#L175
