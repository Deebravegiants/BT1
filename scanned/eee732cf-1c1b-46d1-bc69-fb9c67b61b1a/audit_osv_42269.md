# [M] FFmpeg LCL/ZLIB Video Decoder Information Disclosure via lcldec.c

## Summary
Severity: Medium
Advisory: CVE-2026-66038
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66038
Type: osv

## Details
FFmpeg through 8.1.2, fixed in commit 8670835, contains an information disclosure vulnerability in the LCL/ZLIB video decoder that allows attackers to expose uninitialized heap memory by supplying a valid zlib stream that inflates to fewer bytes than the expected frame size. The zlib_decomp() function in lcldec.c treats short decompression as non-fatal and continues to the RGB24 conversion path, which copies a full frame's worth of rows from the allocation buffer using original frame dimensions, causing uninitialized heap contents including pointer-derived allocator bytes to be copied into the attacker-observable AVFrame output and potentially defeating ASLR in long-lived media processing services.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66038.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66038
- https://www.vulncheck.com/advisories/ffmpeg-lcl-zlib-video-decoder-information-disclosure-via-lcldec-c
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23626
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/e7cbfd1c507b57a806a5825b87d609963e862c8c
