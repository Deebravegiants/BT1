# [C] GHSL-2024-118: GStreamer has a null pointer dereference in gst_gdk_pixbuf_dec_flush

## Summary
Severity: Critical
Advisory: CVE-2024-47613
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47613
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. A null pointer dereference vulnerability has been identified in `gst_gdk_pixbuf_dec_flush` within `gstgdkpixbufdec.c`. This function invokes `memcpy`, using `out_pix` as the destination address. `out_pix` is expected to point to the frame 0 from the frame structure, which is read from the input file. However, in certain situations, it can points to a NULL frame, causing the subsequent call to `memcpy` to attempt writing to the null address (0x00), leading to a null pointer dereference. This vulnerability can result in a Denial of Service (DoS) by triggering a segmentation fault (SEGV). This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0025.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47613.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47613
- https://securitylab.github.com/advisories/GHSL-2024-115_GHSL-2024-118_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8041.patch
