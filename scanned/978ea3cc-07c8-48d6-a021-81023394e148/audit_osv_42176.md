# [M] FFmpeg 0.7.1 - 8.1.2 Out-of-Bounds Read via S/PDIF Muxer spdifenc.c

## Summary
Severity: Medium
Advisory: CVE-2026-64833
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-64833
Type: osv

## Details
FFmpeg versions 0.7.1 through 8.1.2 contain an out-of-bounds read vulnerability in the S/PDIF muxer that allows attackers to access memory beyond buffer boundaries by supplying a crafted DTS stream with a core_size value larger than the actual packet length. Attackers can exploit the missing bounds check in the spdif_header_dts4 function by providing a malicious DTS-HD audio stream during S/PDIF re-muxing to trigger unauthorized memory reads beyond the packet buffer.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64833.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64833
- https://www.vulncheck.com/advisories/ffmpeg-out-of-bounds-read-via-s-pdif-muxer-spdifenc-c
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23661
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/6f80e2765492700622596af720534cef33dd31b4
