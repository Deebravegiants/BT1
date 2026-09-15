# [M] iccDEV ToneMap Writer has NULL Pointer Member Call

## Summary
Severity: Medium
Advisory: CVE-2026-21492
Aliases: GHSA-xpq3-v3jj-mgvx
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21492
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a NULL pointer member call vulnerability. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21492.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-xpq3-v3jj-mgvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-21492
- https://github.com/InternationalColorConsortium/iccDEV/issues/394
- https://github.com/InternationalColorConsortium/iccDEV/commit/b200a629ada310137d6ae5c53fc9e6d91a4b0dae
- https://github.com/InternationalColorConsortium/iccDEV/commit/e72361d215351cbac0002466c4f936e94d6a99e7
- https://github.com/InternationalColorConsortium/iccDEV/pull/401
