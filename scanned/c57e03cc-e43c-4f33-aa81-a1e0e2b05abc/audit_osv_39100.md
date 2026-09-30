# [C] OpenImageIO: Softimage PIC RLE decoder heap buffer overflow — longCount not clamped to image width

## Summary
Severity: Critical
Advisory: CVE-2026-43904
Aliases: GHSA-4499-j545-7q33
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-43904
Type: osv

## Details
OpenImageIO is a toolset for reading, writing, and manipulating image files of any image file format relevant to VFX / animation. Prior to 3.0.18.0 and 3.1.13.0, softimageinput.cpp:469 (mixed RLE) and :345 (pure RLE) do not clamp the run length to remaining scanline width before writing pixels. The raw packet path (line 403) correctly clamps with std::min, but RLE paths skip this check. A crafted .pic file causes heap overflow up to 65535 bytes. This vulnerability is fixed in 3.0.18.0 and 3.1.13.0.

## References
- https://github.com/AcademySoftwareFoundation/OpenImageIO/security/advisories/GHSA-4499-j545-7q33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43904.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43904
