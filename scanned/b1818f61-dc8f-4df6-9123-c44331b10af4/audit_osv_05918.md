# [H] GHSL-2024-243: GStreamer has an integer underflow in extract_cc_from_data leading to OOB-read

## Summary
Severity: High
Advisory: BIT-java-2024-47546
Aliases: BIT-java-min-2024-47546, BIT-jre-2024-47546, CVE-2024-47546
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-47546
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.451

## Details
GStreamer is a library for constructing graphs of media-handling components. An integer underflow has been detected in extract_cc_from_data function within qtdemux.c. In the FOURCC_c708 case, the subtraction atom_length - 8 may result in an underflow if atom_length is less than 8. When that subtraction underflows, *cclen ends up being a large number, and then cclen is passed to g_memdup2 leading to an out-of-bounds (OOB) read. This vulnerability is fixed in 1.24.10.

## References
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8059.patch
- https://gstreamer.freedesktop.org/security/sa-2024-0013.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-47546
- https://securitylab.github.com/advisories/GHSL-2024-243_Gstreamer/
