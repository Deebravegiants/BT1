# [M] LibrePhotos < 1.0.0 - Insecure Direct Object Reference in SetPhotosShared Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-57943
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57943
Type: osv

## Details
LibrePhotos before 1.0.0 contains a broken object level authorization vulnerability in the SetPhotosShared endpoint that allows authenticated users to grant themselves access to other users' private photos by bypassing ownership validation. Attackers can manipulate shared_to relations without proper owner checks to read arbitrary private photos belonging to other users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57943.json
- https://github.com/LibrePhotos/librephotos/releases/tag/1.0.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-57943
- https://www.vulncheck.com/advisories/librephotos-insecure-direct-object-reference-in-setphotosshared-endpoint
- https://github.com/LibrePhotos/librephotos/issues/1860
- https://github.com/LibrePhotos/librephotos/pull/1866
- https://github.com/LibrePhotos/librephotos/commit/325bd1f5fda71c6d56737aa09cfce0cb8106675a
- https://github.com/LibrePhotos/librephotos
