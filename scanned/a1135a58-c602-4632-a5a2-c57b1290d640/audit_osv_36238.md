# [H] iccDEV has heap-buffer-overflow in CIccCLUT::Init() at IccProfLib/IccTagLut.cpp

## Summary
Severity: High
Advisory: CVE-2026-22255
Aliases: GHSA-qv2w-mq3g-73gv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-22255
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a heap-buffer-overflow vulnerability in `CIccCLUT::Init()` at `IccProfLib/IccTagLut.cpp`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22255.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-qv2w-mq3g-73gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-22255
- https://github.com/InternationalColorConsortium/iccDEV/issues/466
- https://github.com/InternationalColorConsortium/iccDEV/pull/469
