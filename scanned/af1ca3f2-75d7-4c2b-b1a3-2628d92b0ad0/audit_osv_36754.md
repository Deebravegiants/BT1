# [H] iccDEV vulnerable to OOB in CIccXform3DLut::Apply()

## Summary
Severity: High
Advisory: CVE-2026-25585
Aliases: GHSA-pmqx-q624-jg6w
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25585
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.3, there is a vulnerability IccCmm.cpp:5793 when reading through index during ICC profile processing. The malformed ICC profile triggers improper array bounds validation in the color management module, resulting in an out-of-bounds read that can lead to memory disclosure or segmentation fault from accessing memory beyond the array boundary. This issue has been patched in version 2.3.1.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25585.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-pmqx-q624-jg6w
- https://nvd.nist.gov/vuln/detail/CVE-2026-25585
- https://github.com/InternationalColorConsortium/iccDEV/issues/552
- https://github.com/InternationalColorConsortium/iccDEV/commit/ba81cd94b9c82b1d3905d45427badbd9d8adfa15
- https://github.com/InternationalColorConsortium/iccDEV/pull/563
