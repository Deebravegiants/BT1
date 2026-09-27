# [M] iccDEV has Type Confusion in CIccTagXmlTagData::ToXml()

## Summary
Severity: Medium
Advisory: CVE-2026-21690
Aliases: GHSA-2f26-vh48-38g6
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21690
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a Type Confusion vulnerability in `CIccTagXmlTagData::ToXml()`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21690.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-2f26-vh48-38g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-21690
- https://github.com/InternationalColorConsortium/iccDEV/issues/393
- https://github.com/InternationalColorConsortium/iccDEV/pull/426
