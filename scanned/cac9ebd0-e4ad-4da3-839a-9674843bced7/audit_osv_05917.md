# [H] GHSL-2024-242: GStreamer has an integer underflow in FOURCC_strf parsing leading to OOB-read

## Summary
Severity: High
Advisory: BIT-java-2024-47545
Aliases: BIT-java-min-2024-47545, BIT-jre-2024-47545, CVE-2024-47545
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-47545
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.451

## Details
GStreamer is a library for constructing graphs of media-handling components. An integer underflow has been detected in qtdemux_parse_trak function within qtdemux.c. During the strf parsing case, the subtraction size -= 40 can lead to a negative integer overflow if it is less than 40. If this happens, the subsequent call to gst_buffer_fill will invoke memcpy with a large tocopy size, resulting in an OOB-read. This vulnerability is fixed in 1.24.10.

## References
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8059.patch
- https://gstreamer.freedesktop.org/security/sa-2024-0010.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-47545
- https://securitylab.github.com/advisories/GHSL-2024-242_Gstreamer/
