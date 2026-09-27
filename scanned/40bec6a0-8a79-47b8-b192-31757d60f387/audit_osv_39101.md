# [C] OpenImageIO: JPEG2000 (OpenJPH) signed integer overflow in buffer allocation

## Summary
Severity: Critical
Advisory: CVE-2026-43905
Aliases: GHSA-pj45-cf3g-28gq
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-43905
Type: osv

## Details
OpenImageIO is a toolset for reading, writing, and manipulating image files of any image file format relevant to VFX / animation. Prior to 3.0.18.0 and 3.1.13.0, jpeg2000input.cpp:395 computes buffer size as const int bufsize = w * h * ch * buffer_bpp using signed 32-bit arithmetic. When the product exceeds INT_MAX, the result wraps to 0 or a small value. m_buf.resize() allocates an undersized buffer, and subsequent pixel write loops cause heap overflow. Conditional on USE_OPENJPH build flag. This vulnerability is fixed in 3.0.18.0 and 3.1.13.0.

## References
- https://github.com/AcademySoftwareFoundation/OpenImageIO/security/advisories/GHSA-pj45-cf3g-28gq
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43905.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43905
