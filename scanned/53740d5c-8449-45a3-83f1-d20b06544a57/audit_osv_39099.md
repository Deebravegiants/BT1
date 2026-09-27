# [C] OpenImageIO: SGI RLE decoder heap buffer overflow OIIO_DASSERT bounds checks are no-ops in release builds

## Summary
Severity: Critical
Advisory: CVE-2026-43903
Aliases: GHSA-jg3q-vm3q-2j35
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-43903
Type: osv

## Details
OpenImageIO is a toolset for reading, writing, and manipulating image files of any image file format relevant to VFX / animation. Prior to 3.0.18.0 and 3.1.13.0, sgiinput.cpp:265,274 use OIIO_DASSERT for bounds checking in the RLE decode loop. In release builds, OIIO_DASSERT compiles to ((void)sizeof(x)) (dassert.h:210), making all bounds checks no-ops. A crafted .sgi file with RLE count exceeding scanline width causes heap buffer overflow and crash. This vulnerability is fixed in 3.0.18.0 and 3.1.13.0.

## References
- https://github.com/AcademySoftwareFoundation/OpenImageIO/security/advisories/GHSA-jg3q-vm3q-2j35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43903.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43903
