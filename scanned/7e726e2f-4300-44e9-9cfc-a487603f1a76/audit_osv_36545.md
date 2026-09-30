# [C] MyTube Allows Unauthorized Database Export by Guest Users

## Summary
Severity: Critical
Advisory: CVE-2026-24139
Aliases: GHSA-hhc3-8q8c-89q7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-24139
Type: osv

## Details
MyTube is a self-hosted downloader and player for several video websites. Versions 1.7.78 and below do not safeguard against authorization bypass, allowing guest users to download the complete application database. The application fails to properly validate user permissions on the database export endpoint, enabling low-privileged users to access sensitive data they should not have permission to view.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24139.json
- https://github.com/franklioxygen/MyTube/security/advisories/GHSA-hhc3-8q8c-89q7
- https://nvd.nist.gov/vuln/detail/CVE-2026-24139
- https://github.com/franklioxygen/MyTube/commit/e271775e27d51b26e54731b7b874447f47a1f280
