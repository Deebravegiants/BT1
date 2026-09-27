# [C] FFmpeg Heap Out-of-Bounds Write via PNG/APNG eXIf Encoder

## Summary
Severity: Critical
Advisory: CVE-2026-66040
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66040
Type: osv

## Details
FFmpeg through 8.1.2, fixed in commit b506faf, contains a heap out-of-bounds write vulnerability in the native PNG and APNG encoders that allows remote attackers to corrupt heap memory by supplying a crafted PNG image with a malicious eXIf chunk. Attackers can craft an eXIf chunk where multiple IFD entries reference the same large value payload, causing canonical serialization to expand the output far beyond the undersized allocation estimated by add_exif_profile_size(), resulting in png_write_chunk() writing tens of thousands of bytes past the buffer boundary, leading to deterministic heap corruption, process crash, and potentially arbitrary code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66040.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66040
- https://www.vulncheck.com/advisories/ffmpeg-heap-out-of-bounds-write-via-png-apng-exif-encoder
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23786
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/b506fafec9a19fcbc2be5271875fd4a63d6615bc
