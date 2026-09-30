# [M] iccDEV has a heap out-of-bounds read in CTiffImg::ReadLine()

## Summary
Severity: Medium
Advisory: CVE-2026-31797
Aliases: GHSA-wh2p-cm3r-7hm3
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-31797
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a heap out-of-bounds read in CTiffImg::ReadLine() when iccApplyProfiles processes a crafted TIFF image, causing memory disclosure or crash. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31797.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-wh2p-cm3r-7hm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-31797
- https://github.com/InternationalColorConsortium/iccDEV/issues/656
- https://github.com/InternationalColorConsortium/iccDEV/pull/659
