# [H] iccDEV has UB runtime error in <icTagTypeSignature>

## Summary
Severity: High
Advisory: CVE-2026-24856
Aliases: GHSA-w585-cv3v-c396
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24856
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Versions prior to 2.3.1.2 have an undefined behavior issue when floating-point NaN values are converted to unsigned short integer types during ICC profile XML parsing potentially corrupting memory structures and enabling arbitrary code execution. This vulnerability affects users of the iccDEV library who process ICC color profiles. ICC Profile Injection vulnerabilities arise when user-controllable input is incorporated into ICC profile data or other structured binary blobs in an unsafe manner. Version 2.3.1.2 contains a fix for the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24856.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-w585-cv3v-c396
- https://nvd.nist.gov/vuln/detail/CVE-2026-24856
- https://github.com/InternationalColorConsortium/iccDEV/issues/532
- https://github.com/InternationalColorConsortium/iccDEV/commit/5e53a5d25923b7794ba44e390e9b35d391f2b9c1
- https://github.com/InternationalColorConsortium/iccDEV/pull/541
