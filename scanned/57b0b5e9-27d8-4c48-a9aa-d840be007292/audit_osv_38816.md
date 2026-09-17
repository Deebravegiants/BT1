# [C] OpenColorIO vulnerable to stack buffer overflow via unbounded `sscanf %s` in Spi3D (.spi3d) LUT parser

## Summary
Severity: Critical
Advisory: CVE-2026-42450
Aliases: GHSA-rxp3-rrgx-f547
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-42450
Type: osv

## Details
OpenColorIO is a color management framework for visual effects and animation. Prior to version 2.5.2, `FileFormatSpi3D.cpp:163` uses `sscanf` with `%s` into 64-byte stack buffers when parsing LUT data lines. Input comes from `lineBuffer[4096]`, so a crafted .spi3d file can overflow by ~4000 bytes on non-Windows. Version 2.5.2 fixes the issue.

## References
- https://github.com/AcademySoftwareFoundation/OpenColorIO/releases/tag/v2.5.2
- https://github.com/AcademySoftwareFoundation/OpenColorIO/security/advisories/GHSA-rxp3-rrgx-f547
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42450
