# [H] CVE-2025-60474

## Summary
Severity: High
Advisory: CVE-2025-60474
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2025-60474
Type: osv

## Details
A buffer overflow in the gf_media_import function (/media_tools/av_parsers.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted input.

## References
- http://www.openwall.com/lists/oss-security/2026/06/27/5
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/38/38_gf_media_import_media_tools_media_import_c_1297
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/38/README.md
- https://infosec.exchange/@sigdevel/116780566799952592
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60474.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60474
- https://github.com/gpac/gpac/issues/3287
- https://github.com/gpac/gpac/commit/bd7fd6be546e0cd9e599c6b262c338c5f2ecec5c
