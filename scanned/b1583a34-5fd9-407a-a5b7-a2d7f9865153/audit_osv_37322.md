# [M] iccDEV has a heap out-of-bounds read in CIccPcsXform::pushXYZConvert()

## Summary
Severity: Medium
Advisory: CVE-2026-30982
Aliases: GHSA-7ww3-h4w6-x5hf
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30982
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a heap out-of-bounds read in CIccPcsXform::pushXYZConvert() causing crash and potentially leaking memory contents. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30982.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-7ww3-h4w6-x5hf
- https://nvd.nist.gov/vuln/detail/CVE-2026-30982
- https://github.com/InternationalColorConsortium/iccDEV/issues/625
- https://github.com/InternationalColorConsortium/iccDEV/pull/632
