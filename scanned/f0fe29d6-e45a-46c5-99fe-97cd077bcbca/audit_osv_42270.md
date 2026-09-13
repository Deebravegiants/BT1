# [C] FFmpeg MACE6 Audio Decoder Heap Out-of-Bounds Write via CAF File

## Summary
Severity: Critical
Advisory: CVE-2026-66039
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66039
Type: osv

## Details
FFmpeg through 8.1.2, fixed in commit aafb5c6, contains a signed integer overflow vulnerability in the MACE6 audio decoder that allows attackers to corrupt heap memory by supplying a crafted CAF file with a malicious bytes_per_packet value. Attackers can craft a CAF file with oversized bytes_per_packet and frames_per_packet values in the desc chunk to trigger an integer overflow in mace_decode_frame() during output sample count computation, resulting in an undersized buffer allocation and heap out-of-bounds write that could enable code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66039.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66039
- https://www.vulncheck.com/advisories/ffmpeg-mace6-audio-decoder-heap-out-of-bounds-write-via-caf-file
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23631
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/aafb5c655edc76a753275c383ebb139feb032718
