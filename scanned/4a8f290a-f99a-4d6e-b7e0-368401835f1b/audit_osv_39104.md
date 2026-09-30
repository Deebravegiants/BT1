# [H] OpenImageIO: Signed integer overflow in SwapRGBABytes loop index leads to out-of-bounds read/write in DPX ABGR decoder

## Summary
Severity: High
Advisory: CVE-2026-43909
Aliases: GHSA-g267-j53j-5258
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-43909
Type: osv

## Details
OpenImageIO is a toolset for reading, writing, and manipulating image files of any image file format relevant to VFX / animation. Prior to 3.0.18.0 and 3.1.13.0, a signed 32-bit integer overflow in the loop index expression i * 4 inside SwapRGBABytes() causes the function to compute a large negative pointer offset when processing kABGR DPX images with large dimensions. The immediate crash is an out-of-bounds read (the memcpy at line 45 reads from &input[i * 4] first), but the subsequent write operations at lines 46–49 target the same wrapped offset — making this a combined OOB read+write primitive. This vulnerability is fixed in 3.0.18.0 and 3.1.13.0.

## References
- https://github.com/AcademySoftwareFoundation/OpenImageIO/security/advisories/GHSA-g267-j53j-5258
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43909.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43909
