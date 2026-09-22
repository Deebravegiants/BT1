# [M] iccDEV: HBO in CIccMpeSpectralMatrix::Describe()

## Summary
Severity: Medium
Advisory: CVE-2026-34534
Aliases: GHSA-7x9w-g476-wcc2
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34534
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a crafted ICC profile can trigger a heap-buffer-overflow (HBO) in CIccMpeSpectralMatrix::Describe(). The issue is observable under AddressSanitizer as an out-of-bounds heap read when running iccDumpProfile on a malicious profile. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34534.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-7x9w-g476-wcc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34534
- https://github.com/InternationalColorConsortium/iccDEV/issues/665
- https://github.com/InternationalColorConsortium/iccDEV/pull/682
