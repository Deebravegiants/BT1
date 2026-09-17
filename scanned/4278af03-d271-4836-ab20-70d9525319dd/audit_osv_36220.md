# [H] iccDEV has heap-buffer-overflow in CIccProfileXml::ParseBasic() at IccXML/IccLibXML/IccProfileXml.cpp

## Summary
Severity: High
Advisory: CVE-2026-22046
Aliases: GHSA-7v4q-mhr2-hj7r
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-22046
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a heap-buffer-overflow vulnerability in `CIccProfileXml::ParseBasic()` at `IccXML/IccLibXML/IccProfileXml.cpp`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22046.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-7v4q-mhr2-hj7r
- https://nvd.nist.gov/vuln/detail/CVE-2026-22046
- https://github.com/InternationalColorConsortium/iccDEV/issues/448
- https://github.com/InternationalColorConsortium/iccDEV/pull/451
