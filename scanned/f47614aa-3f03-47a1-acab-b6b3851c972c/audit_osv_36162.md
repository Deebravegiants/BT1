# [M] iccDEV has Null Pointer Dereference in CIccProfile::CheckTagTypes()

## Summary
Severity: Medium
Advisory: CVE-2026-21680
Aliases: GHSA-mgp7-w4w3-mhx4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21680
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of International Color Consortium (ICC) color management profiles. Versions prior to 2.3.1.2 have a NULL pointer dereference vulnerability. This vulnerability affects users of the iccDEV library who process ICC color profiles. Version 2.3.1.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21680.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-mgp7-w4w3-mhx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-21680
- https://github.com/InternationalColorConsortium/iccDEV/issues/322
- https://github.com/InternationalColorConsortium/iccDEV/pull/325
