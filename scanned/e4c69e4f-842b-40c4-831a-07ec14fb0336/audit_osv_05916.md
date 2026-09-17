# [H] GHSL-2024-238: GStreamer has NULL-pointer dereferences in MP4/MOV demuxer CENC handling

## Summary
Severity: High
Advisory: BIT-java-2024-47544
Aliases: BIT-java-min-2024-47544, BIT-jre-2024-47544, CVE-2024-47544
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-47544
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.451

## Details
GStreamer is a library for constructing graphs of media-handling components. The function qtdemux_parse_sbgp in qtdemux.c is affected by a null dereference vulnerability. This vulnerability is fixed in 1.24.10.

## References
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8059.patch
- https://gstreamer.freedesktop.org/security/sa-2024-0011.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-47544
- https://securitylab.github.com/advisories/GHSL-2024-238_Gstreamer/
