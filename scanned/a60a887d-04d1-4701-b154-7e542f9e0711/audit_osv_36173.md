# [M] iccDEV has Type Confusion in CIccTag:IsTypeCompressed()

## Summary
Severity: Medium
Advisory: CVE-2026-21691
Aliases: GHSA-c9q5-x498-jv92
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21691
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a Type Confusion vulnerability in `CIccTag:IsTypeCompressed()`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21691.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-c9q5-x498-jv92
- https://nvd.nist.gov/vuln/detail/CVE-2026-21691
- https://github.com/InternationalColorConsortium/iccDEV/issues/392
- https://github.com/InternationalColorConsortium/iccDEV/pull/426
