# [H] iccDEV Has Type Confusion in CIccTagEmbeddedHeightImage::Validate()

## Summary
Severity: High
Advisory: CVE-2026-25503
Aliases: GHSA-pf84-4c7q-x764
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25503
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, type confusion allowed malformed ICC profiles to trigger undefined behavior when loading invalid icImageEncodingType values causing denial of service. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25503.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-pf84-4c7q-x764
- https://nvd.nist.gov/vuln/detail/CVE-2026-25503
- https://github.com/InternationalColorConsortium/iccDEV/issues/539
- https://github.com/InternationalColorConsortium/iccDEV/commit/353e6517a31cb6ac9fdd44ac0103bc2fadb25175
- https://github.com/InternationalColorConsortium/iccDEV/pull/547
