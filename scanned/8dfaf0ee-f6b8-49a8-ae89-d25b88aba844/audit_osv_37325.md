# [M] iccDEV has a heap-based buffer overflow write in CIccCLUT::Interp3d()

## Summary
Severity: Medium
Advisory: CVE-2026-30986
Aliases: GHSA-w3g9-rmvh-49gh
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30986
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a heap-based buffer overflow write in CIccMatrixMath::SetRange() causing memory corruption or crash. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30986.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-w3g9-rmvh-49gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-30986
- https://github.com/InternationalColorConsortium/iccDEV/issues/620
- https://github.com/InternationalColorConsortium/iccDEV/pull/637
