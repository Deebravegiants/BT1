# [M] GHSL-2024-250: Streamer NULL-pointer dereferences and out-of-bounds reads in Matroska/WebM demuxer

## Summary
Severity: Medium
Advisory: CVE-2024-47602
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47602
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. A null pointer dereference vulnerability has been discovered in the gst_matroska_demux_add_wvpk_header function within matroska-demux.c. This function does not properly check the validity of the stream->codec_priv pointer in the following code. If stream->codec_priv is NULL, the call to GST_READ_UINT16_LE will attempt to dereference a null pointer, leading to a crash of the application. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0019.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47602.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47602
- https://securitylab.github.com/advisories/GHSL-2024-250_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8057.patch
