# [C] GHSL-2024-261: GStreamer has an OOB-read in parse_ds64

## Summary
Severity: Critical
Advisory: BIT-java-2024-47775
Aliases: BIT-java-min-2024-47775, BIT-jre-2024-47775, CVE-2024-47775
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2024-47775
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.451

## Details
GStreamer is a library for constructing graphs of media-handling components. An OOB-read vulnerability has been found in the parse_ds64 function within gstwavparse.c. The parse_ds64 function does not check that the buffer buf contains sufficient data before attempting to read from it, doing multiple GST_READ_UINT32_LE operations without performing boundary checks. This can lead to an OOB-read when buf is smaller than expected. This vulnerability allows reading beyond the bounds of the data buffer, potentially leading to a crash (denial of service) or the leak of sensitive data. This vulnerability is fixed in 1.24.10.

## References
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8042.patch
- https://gstreamer.freedesktop.org/security/sa-2024-0027.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-47775
- https://securitylab.github.com/advisories/GHSL-2024-261_Gstreamer/
