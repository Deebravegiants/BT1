# [M] Heap-buffer-overflow write in FFmpeg SANM decoding due to lack of bounds-checking in old_codec48

## Summary
Severity: Medium
Advisory: CVE-2025-59730
CVSS: 6.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:L/UI:P/VC:L/VI:H/VA:N/SC:L/SI:H/SA:N)
Published: 2025-10-06
Source: https://osv.dev/vulnerability/CVE-2025-59730
Type: osv

## Details
When decoding a frame for a SANM file (ANIM v0 variant), the decoded data can be larger than the buffer allocated for it.

Frames encoded with codec 48 can specify their resolution (width x height). A buffer of appropriate size is allocated depending on the resolution.

This codec can encode the frame contents using a run-length encoding algorithm. There are no checks that the decoded frame fits in the allocated buffer, leading to a heap-buffer-overflow.

process_frame_obj initializes the buffers based on the frame resolution:



We recommend upgrading to version 8.0 or beyond.

## References
- https://issuetracker.google.com/434637586
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59730.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59730
- https://git.ffmpeg.org/ffmpeg.git
