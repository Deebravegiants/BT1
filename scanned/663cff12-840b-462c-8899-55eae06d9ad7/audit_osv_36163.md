# [H] iccDEV has Undefined Behavior runtime error: nan is outside the range .. IccProfLib/IccTagBasic.cpp

## Summary
Severity: High
Advisory: CVE-2026-21681
Aliases: GHSA-v4qq-v3c3-x62x
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21681
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a Undefined Behavior runtime error. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21681.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-v4qq-v3c3-x62x
- https://nvd.nist.gov/vuln/detail/CVE-2026-21681
- https://github.com/InternationalColorConsortium/iccDEV/pull/269
