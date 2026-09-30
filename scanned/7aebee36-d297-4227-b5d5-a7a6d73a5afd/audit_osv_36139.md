# [M] iccDEV has Undefined Behavior - Null Pointer Passed to memcpy() in CIccTagSparseMatrixArray

## Summary
Severity: Medium
Advisory: CVE-2026-21503
Aliases: GHSA-h554-qrfh-53gx
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21503
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV has undefined behavior due to a null pointer passed to memcpy() in CIccTagSparseMatrixArray. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21503.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-h554-qrfh-53gx
- https://nvd.nist.gov/vuln/detail/CVE-2026-21503
- https://github.com/InternationalColorConsortium/iccDEV/issues/367
- https://github.com/InternationalColorConsortium/iccDEV/commit/55259a6395c4f6124b5d0e38469c77412926bd3d
- https://github.com/InternationalColorConsortium/iccDEV/pull/417
