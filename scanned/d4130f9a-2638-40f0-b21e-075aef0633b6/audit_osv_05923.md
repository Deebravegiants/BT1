# [C] GHSL-2024-260: GStreamer has a OOB-read in gst_wavparse_cue_chunk

## Summary
Severity: Critical
Advisory: BIT-java-2024-47776
Aliases: BIT-java-min-2024-47776, BIT-jre-2024-47776, CVE-2024-47776
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-47776
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.451

## Details
GStreamer is a library for constructing graphs of media-handling components. An OOB-read has been discovered in gst_wavparse_cue_chunk within gstwavparse.c. The vulnerability happens due to a discrepancy between the size of the data buffer and the size value provided to the function. This mismatch causes the comparison  if (size < 4 + ncues * 24) to fail in some cases, allowing the subsequent loop to access beyond the bounds of the data buffer. The root cause of this discrepancy stems from a miscalculation when clipping the chunk size based on upstream data size. This vulnerability allows reading beyond the bounds of the data buffer, potentially leading to a crash (denial of service) or the leak of sensitive data. This vulnerability is fixed in 1.24.10.

## References
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8042.patch
- https://gstreamer.freedesktop.org/security/sa-2024-0027.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-47776
- https://securitylab.github.com/advisories/GHSL-2024-260_Gstreamer/
