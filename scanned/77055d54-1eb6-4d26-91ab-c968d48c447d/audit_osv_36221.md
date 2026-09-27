# [H] iccDEV has heap-buffer-overflow in SIccCalcOp::Describe() at IccProfLib/IccMpeCalc.cpp

## Summary
Severity: High
Advisory: CVE-2026-22047
Aliases: GHSA-22q7-8347-79m5
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-22047
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a heap-buffer-overflow vulnerability in `SIccCalcOp::Describe()` at `IccProfLib/IccMpeCalc.cpp`. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22047.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-22q7-8347-79m5
- https://nvd.nist.gov/vuln/detail/CVE-2026-22047
- https://github.com/InternationalColorConsortium/iccDEV/issues/454
- https://github.com/InternationalColorConsortium/iccDEV/pull/459
