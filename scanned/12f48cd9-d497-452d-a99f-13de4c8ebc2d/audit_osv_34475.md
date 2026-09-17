# [M] CVE-2025-60486

## Summary
Severity: Medium
Advisory: CVE-2025-60486
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2025-60486
Type: osv

## Details
A heap use-after-free in the dasher_process function (/filters/dasher.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted MPEG-2 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/01/12
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/53/README.md
- https://infosec.exchange/@sigdevel/116662544397024289
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60486.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60486
- https://github.com/gpac/gpac/issues/3314
- https://github.com/gpac/gpac/commit/e6d01820d7bf3967d931fedb379ee5f209bc133b
