# [M] ManageIQ vulnerable to DoS Attack when  creating TimeProfiles

## Summary
Severity: Medium
Advisory: CVE-2026-22598
Aliases: GHSA-m832-x3g8-63j3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2026-22598
Type: osv

## Details
ManageIQ is an open-source management platform. A flaw was found in the ManageIQ API prior to version radjabov-2 where a malformed TimeProfile could be created causing later UI and API requests to timeout leading to a Denial of Service. Version radjabov-2 contains a patch. One may also apply the patch manually.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22598.json
- https://github.com/ManageIQ/manageiq/security/advisories/GHSA-m832-x3g8-63j3
- https://nvd.nist.gov/vuln/detail/CVE-2026-22598
- https://github.com/ManageIQ/manageiq/commit/79cef10c7d0278d8a37c3f547c426948180df4df.patch
- https://github.com/ManageIQ/manageiq/commit/86132851257d73ed9e31a88315e47a8a2b838113
