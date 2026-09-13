# [M] GHSL-2024-247: GStreamer Insufficient error handling in JPEG decoder that can lead to NULL-pointer dereferences

## Summary
Severity: Medium
Advisory: CVE-2024-47599
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47599
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. A null pointer dereference vulnerability has been discovered in the gst_jpeg_dec_negotiate function in gstjpegdec.c. This function does not check for a NULL return value from gst_video_decoder_set_output_state. When this happens, dereferences of the outstate pointer will lead to a null pointer dereference. This vulnerability can result in a Denial of Service (DoS) by triggering a segmentation fault (SEGV). This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0016.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00035.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47599.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47599
- https://securitylab.github.com/advisories/GHSL-2024-247_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8040.patch
