# [M] FreeRDP RDPGFX ResetGraphics race leads to use-after-free in SDL client (sdl->primary)

## Summary
Severity: Medium
Advisory: CVE-2026-22851
Aliases: GHSA-8g87-6pvc-wh99
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22851
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.20.1, a race condition between the RDPGFX dynamic virtual channel thread and the SDL render thread leads to a heap use-after-free. Specifically, an escaped pointer to sdl->primary (SDL_Surface) is accessed after it has been freed during RDPGFX ResetGraphics handling. This vulnerability is fixed in 3.20.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.20.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22851.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-8g87-6pvc-wh99
- https://nvd.nist.gov/vuln/detail/CVE-2026-22851
