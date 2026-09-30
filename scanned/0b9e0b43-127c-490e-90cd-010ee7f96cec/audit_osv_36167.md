# [H] iccDEV has Undefined Behavior in CIccTagLut16::Read()

## Summary
Severity: High
Advisory: CVE-2026-21685
Aliases: GHSA-c3xr-6687-5c8p
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21685
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have Undefined Behavior in `CIccTagLut16::Read()`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21685.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-c3xr-6687-5c8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-21685
- https://github.com/InternationalColorConsortium/iccDEV/issues/213
- https://github.com/InternationalColorConsortium/iccDEV/pull/223
