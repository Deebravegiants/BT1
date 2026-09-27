# [M] GHSL-2024-249: GStreamer has a NULL-pointer dereference in Matroska/WebM demuxer

## Summary
Severity: Medium
Advisory: CVE-2024-47601
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47601
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. A null pointer dereference vulnerability has been discovered in the gst_matroska_demux_parse_blockgroup_or_simpleblock function within matroska-demux.c. This function does not properly check the validity of the GstBuffer *sub pointer before performing dereferences. As a result, null pointer dereferences may occur. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0020.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47601.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47601
- https://securitylab.github.com/advisories/GHSL-2024-249_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8057.patch
