# [H] iccDEV has Integer Overflow/Underflow in CIccXmlArrayType::ParseTextCountNum()

## Summary
Severity: High
Advisory: CVE-2026-21673
Aliases: GHSA-g66g-f82c-vgm6
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21673
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1 and below have overflows and underflows in  CIccXmlArrayType::ParseTextCountNum(). This vulnerability affects users of the iccDEV library who process ICC color profiles. This issue is fixed in version 2.3.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21673.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-g66g-f82c-vgm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-21673
- https://github.com/InternationalColorConsortium/iccDEV/issues/243
- https://github.com/InternationalColorConsortium/iccDEV/commit/32740802ee14418bd14c429d7e2f142d92cd5c4f
