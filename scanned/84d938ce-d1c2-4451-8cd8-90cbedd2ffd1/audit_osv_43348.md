# [M] VLC media player 3.0.0 through 3.0.23 Heap Out-of-Bounds Read via Unterminated RealRTSP Response Line

## Summary
Severity: Medium
Advisory: CVE-2026-73324
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-73324
Type: osv

## Details
VLC media player copies an RTSP response line into a fixed buffer without guaranteeing termination and then treats that buffer as a C string. RtspReadLine in modules/access/rtsp/access.c calls strncpy with the full buffer length, which writes no terminator when the source line is at least as long as the destination, and rtsp_get in modules/access/rtsp/rtsp.c allocates that buffer as BUF_SIZE bytes and passes it to strdup. When a server returns a line of 4096 bytes or more, strdup measures its length past the end of the allocation and copies adjacent heap bytes until an incidental zero byte. Because the affected line is the Session header, the disclosed bytes are retained as the session identifier and sent back to the server on every subsequent request, so the operator of a hostile server reads heap memory from the client rather than inferring it. The attacker controls the line length and therefore how far the read runs. A single playlist entry naming a realrtsp URL is sufficient. The module is a build-time option, disabled in some distribution packages and enabled in the official VideoLAN builds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73324.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73324
- https://www.vulncheck.com/advisories/vlc-media-player-3.0.0-through-3.0.23-heap-out-of-bounds-read-via-unterminated-realrtsp-response-line
- https://github.com/videolan/vlc
- https://github.com/videolan/vlc/blob/3.0.23/modules/access/rtsp/access.c
- https://github.com/videolan/vlc/blob/3.0.23/modules/access/rtsp/rtsp.c
