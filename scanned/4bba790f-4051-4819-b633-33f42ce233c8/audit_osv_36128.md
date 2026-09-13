# [M] iccDEV has heap buffer overflow in CIccTagLut16::Validate()

## Summary
Severity: Medium
Advisory: CVE-2026-21490
Aliases: GHSA-9q9c-699q-xr2q
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21490
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. A vulnerability present in versions prior to 2.3.1.2 affects users of the iccDEV library who process ICC color profiles. It results in heap buffer overflow in `CIccTagLut16::Validate()`. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21490.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-9q9c-699q-xr2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-21490
- https://github.com/InternationalColorConsortium/iccDEV/issues/397
- https://github.com/InternationalColorConsortium/iccDEV/commit/7c2cb719a9de1c00844e457e070d657314383ee3
- https://github.com/InternationalColorConsortium/iccDEV/commit/e91fe722ac54ce497d410153e7405090e0565d7b
