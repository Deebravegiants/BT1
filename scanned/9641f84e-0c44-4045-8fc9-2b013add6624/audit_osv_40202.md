# [M] CVE-2026-50810

## Summary
Severity: Medium
Advisory: CVE-2026-50810
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-50810
Type: osv

## Details
A NULL pointer dereference in smooth_parse_stream_index() in src/media_tools/mpd.c in GPAC master HEAD before commit b35c61f104b85fbb16520ac2838d5d2ef70845b5 allows attackers to cause a denial of service

## References
- https://gist.github.com/junius-sec/0c67bf67a268ff8861100bfc132e801c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50810.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50810
- https://github.com/gpac/gpac/issues/3507
- https://github.com/gpac/gpac/commit/b35c61f104b85fbb16520ac2838d5d2ef70845b5
