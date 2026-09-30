# [C] OpenImageIO: HEIF Heap overflow

## Summary
Severity: Critical
Advisory: CVE-2026-43906
Aliases: GHSA-gmrp-x952-3m66
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-43906
Type: osv

## Details
OpenImageIO is a toolset for reading, writing, and manipulating image files of any image file format relevant to VFX / animation. Prior to 3.0.18.0 and 3.1.13.0, a heap-based buffer overflow in the HEIF decoder of OpenImageIO allows out-of-bounds writes via crafted images due to a subimage metadata mismatch, leading to memory corruption and potential code execution. This vulnerability is fixed in 3.0.18.0 and 3.1.13.0.

## References
- https://github.com/AcademySoftwareFoundation/OpenImageIO/security/advisories/GHSA-gmrp-x952-3m66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43906.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43906
