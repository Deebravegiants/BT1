# [H] GHSL-2024-258: GStreamer has an OOB-read in gst_wavparse_adtl_chunk

## Summary
Severity: High
Advisory: BIT-java-2024-47778
Aliases: BIT-java-min-2024-47778, BIT-jre-2024-47778, CVE-2024-47778
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-47778
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.451

## Details
GStreamer is a library for constructing graphs of media-handling components. An OOB-read vulnerability has been discovered in gst_wavparse_adtl_chunk within gstwavparse.c. This vulnerability arises due to insufficient validation of the size parameter, which can exceed the bounds of the data buffer. As a result, an OOB read occurs in the following while loop. This vulnerability can result in reading up to 4GB of process memory or potentially causing a segmentation fault (SEGV) when accessing invalid memory. This vulnerability is fixed in 1.24.10.

## References
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8042.patch
- https://gstreamer.freedesktop.org/security/sa-2024-0027.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-47778
- https://securitylab.github.com/advisories/GHSL-2024-258_Gstreamer/
