# [H] iccDEV has heap-buffer-overflow in CIccXmlArrayType::ParseText()

## Summary
Severity: High
Advisory: CVE-2026-21682
Aliases: GHSA-jq9m-54gr-c56c
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21682
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a heap-buffer-overflow in `CIccXmlArrayType::ParseText()`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21682.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-jq9m-54gr-c56c
- https://nvd.nist.gov/vuln/detail/CVE-2026-21682
- https://github.com/InternationalColorConsortium/iccDEV/issues/178
- https://github.com/InternationalColorConsortium/iccDEV/pull/229
