# [M] Heap Buffer Overflow in iccDEV ToneMap Parser

## Summary
Severity: Medium
Advisory: CVE-2026-21504
Aliases: GHSA-rqp9-r53c-3m9h
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21504
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to heap buffer overflow in the ToneMap parser. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/InternationalColorConsortium/iccDEV/blob/798be59011649a26a529600cc3cd56437634d3d0/IccProfLib/IccMpeBasic.cpp#L4557
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21504.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-rqp9-r53c-3m9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-21504
- https://github.com/InternationalColorConsortium/iccDEV/issues/366
- https://github.com/InternationalColorConsortium/iccDEV/commit/14fe3785e6b1f9992375b2a24617a0d7f6a70f95
- https://github.com/InternationalColorConsortium/iccDEV/commit/23a38f83f2a5874a1c4427df59ec342af3277cad
- https://github.com/InternationalColorConsortium/iccDEV/pull/415
