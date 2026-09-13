# [M] Flatpak affected by arbitrary file deletion on the host filesystem

## Summary
Severity: Medium
Advisory: CVE-2026-34079
Aliases: GHSA-p29x-r292-46pp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-34079
Type: osv

## Details
Flatpak is a Linux application sandboxing and distribution framework. Prior to 1.16.4, the caching for ld.so removes outdated cache files without properly checking that the app controlled path to the outdated cache is in the cache directory. This allows Flatpak apps  to delete arbitrary files on the host. This vulnerability is fixed in 1.16.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34079.json
- https://github.com/flatpak/flatpak/security/advisories/GHSA-p29x-r292-46pp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34079
