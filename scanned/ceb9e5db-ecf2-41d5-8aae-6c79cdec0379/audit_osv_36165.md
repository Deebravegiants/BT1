# [H] iccDEV has Type Confusion in icStatusCMM::CIccEvalCompare::EvaluateProfile()

## Summary
Severity: High
Advisory: CVE-2026-21683
Aliases: GHSA-f2wp-j3fr-938w
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21683
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a Type Confusion vulnerability in `icStatusCMM::CIccEvalCompare::EvaluateProfile()`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21683.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-f2wp-j3fr-938w
- https://nvd.nist.gov/vuln/detail/CVE-2026-21683
- https://github.com/InternationalColorConsortium/iccDEV/issues/183
- https://github.com/InternationalColorConsortium/iccDEV/pull/228
