# [M] iccDEV: SBO in CIccTagFixedNum::GetValues()

## Summary
Severity: Medium
Advisory: CVE-2026-34555
Aliases: GHSA-983c-rgh5-4982
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34555
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, there is a stack-buffer-overflow (SBO) in CIccTagFixedNum<>::GetValues() and a related bug chain. The primary crash is an AddressSanitizer-reported WRITE of size 4 that overflows a 4-byte stack variable (rv) via the call chain CIccTagFixedNum::GetValues() -> CIccTagStruct::GetElemNumberValue(). This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34555.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-983c-rgh5-4982
- https://nvd.nist.gov/vuln/detail/CVE-2026-34555
- https://github.com/InternationalColorConsortium/iccDEV/issues/696
- https://github.com/InternationalColorConsortium/iccDEV/issues/697
- https://github.com/InternationalColorConsortium/iccDEV/issues/698
- https://github.com/InternationalColorConsortium/iccDEV/issues/703
- https://github.com/InternationalColorConsortium/iccDEV/pull/739
