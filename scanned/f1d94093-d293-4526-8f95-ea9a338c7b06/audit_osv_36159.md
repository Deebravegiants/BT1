# [H] iccDEV has Undefined Behavior in CIccCLUT::Init()

## Summary
Severity: High
Advisory: CVE-2026-21677
Aliases: GHSA-95w5-jvqf-3994
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21677
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1 and below have Undefined Behavior in its CIccCLUT::Init function which initializes and sets the size of a CLUT. This issue is fixed in version 2.3.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21677.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-95w5-jvqf-3994
- https://nvd.nist.gov/vuln/detail/CVE-2026-21677
- https://github.com/InternationalColorConsortium/iccDEV/issues/181
- https://github.com/InternationalColorConsortium/iccDEV/commit/201125fbda22c8e4ea95800a6b427093fa4b8a22
