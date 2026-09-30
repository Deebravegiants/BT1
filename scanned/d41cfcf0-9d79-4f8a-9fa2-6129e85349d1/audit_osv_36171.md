# [M] iccDEV has Type Confusion in CIccProfileXml::ParseBasic() at IccXML/IccLibXML/IccProfileXml.cpp

## Summary
Severity: Medium
Advisory: CVE-2026-21689
Aliases: GHSA-5rqc-w93q-589m
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21689
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a Type Confusion vulnerability in `CIccProfileXml::ParseBasic()` at `IccXML/IccLibXML/IccProfileXml.cpp`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21689.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-5rqc-w93q-589m
- https://nvd.nist.gov/vuln/detail/CVE-2026-21689
- https://github.com/InternationalColorConsortium/iccDEV/issues/382
- https://github.com/InternationalColorConsortium/iccDEV/pull/423
