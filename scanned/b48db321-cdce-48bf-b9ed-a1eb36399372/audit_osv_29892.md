# [M] GHSL-2024-235: GStreamer ID3v2 parser out-of-bounds read and NULL-pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2024-47542
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47542
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. A null pointer dereference has been discovered in the id3v2_read_synch_uint function, located in id3v2.c. If id3v2_read_synch_uint is called with a null work->hdr.frame_data, the pointer guint8 *data is accessed without validation, resulting in a null pointer dereference. This vulnerability can result in a Denial of Service (DoS) by triggering a segmentation fault (SEGV). This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0008.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00021.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47542.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47542
- https://securitylab.github.com/advisories/GHSL-2024-235_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8033.patch
