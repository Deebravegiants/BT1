# [M] iccDEV: HBO in CTiffImg::WriteLine()

## Summary
Severity: Medium
Advisory: CVE-2026-34539
Aliases: GHSA-4f3j-q8mm-5hr6
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34539
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a crafted ICC profile and TIFF input can trigger a heap-buffer-overflow (HBO) in CTiffImg::WriteLine(). The issue is observable under AddressSanitizer as an out-of-bounds heap read when running iccSpecSepToTiff on a malicious .icc + .tif pair, leading to a crash during TIFF strip writing. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34539.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-4f3j-q8mm-5hr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-34539
- https://github.com/InternationalColorConsortium/iccDEV/issues/672
- https://github.com/InternationalColorConsortium/iccDEV/pull/686
