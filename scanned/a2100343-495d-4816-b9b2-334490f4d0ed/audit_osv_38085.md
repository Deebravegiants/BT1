# [M] iccDEV: HBO in CIccApplyCmmSearch::costFunc()

## Summary
Severity: Medium
Advisory: CVE-2026-34554
Aliases: GHSA-hqc7-5pgc-9672
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34554
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a heap-buffer-overflow (HBO) in CIccApplyCmmSearch::costFunc() can be triggered via malformed JSON configuration input to the iccApplySearch tool. AddressSanitizer reports an out-of-bounds READ of size 8 originating from CIccApplyCmmSearch::costFunc(CIccSearchVec&) at IccProfLib/IccCmmSearch.cpp:112:5. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34554.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-hqc7-5pgc-9672
- https://nvd.nist.gov/vuln/detail/CVE-2026-34554
- https://github.com/InternationalColorConsortium/iccDEV/issues/700
- https://github.com/InternationalColorConsortium/iccDEV/pull/738
