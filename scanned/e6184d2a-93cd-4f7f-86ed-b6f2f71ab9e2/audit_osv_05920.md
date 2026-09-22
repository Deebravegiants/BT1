# [C] GHSL-2024-245: GStreamer has an OOB-read in qtdemux_parse_samples

## Summary
Severity: Critical
Advisory: BIT-java-2024-47597
Aliases: BIT-java-min-2024-47597, BIT-jre-2024-47597, CVE-2024-47597
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-47597
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.451

## Details
GStreamer is a library for constructing graphs of media-handling components. An OOB-read has been detected in the function qtdemux_parse_samples within qtdemux.c. This issue arises when the function qtdemux_parse_samples reads data beyond the boundaries of the stream->stco buffer. The following code snippet shows the call to qt_atom_parser_get_offset_unchecked, which leads to the OOB-read when parsing the provided GHSL-2024-245_crash1.mp4 file. This issue may lead to read up to 8 bytes out-of-bounds. This vulnerability is fixed in 1.24.10.

## References
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8059.patch
- https://gstreamer.freedesktop.org/security/sa-2024-0012.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-47597
- https://securitylab.github.com/advisories/GHSL-2024-245_Gstreamer/
