# [M] Stack Overflow in iccDEV Calculator Parser

## Summary
Severity: Medium
Advisory: CVE-2026-21501
Aliases: GHSA-x7hw-h22p-2x4w
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21501
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to stack overflow in the calculator parser. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/InternationalColorConsortium/iccDEV/blob/8e71f0a701abcbd554725ba7b70258203e682a61/IccProfLib/IccMpeCalc.cpp#L4588
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21501.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-x7hw-h22p-2x4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-21501
- https://github.com/InternationalColorConsortium/iccDEV/issues/365
- https://github.com/InternationalColorConsortium/iccDEV/commit/798be59011649a26a529600cc3cd56437634d3d0
- https://github.com/InternationalColorConsortium/iccDEV/commit/f3056ed99935d479091470127ad16f8be1912bb7
- https://github.com/InternationalColorConsortium/iccDEV/pull/413
