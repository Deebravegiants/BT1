# [H] ALPINE-CVE-2024-47542

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-47542
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47542
Type: osv

## Affected
- Alpine:v3.20: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.21: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.22: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.23: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.24: `gst-plugins-base` — affected >=0 <1.24.10-r0

## Details
GStreamer is a library for constructing graphs of media-handling components. A null pointer dereference has been discovered in the id3v2_read_synch_uint function, located in id3v2.c. If id3v2_read_synch_uint is called with a null work->hdr.frame_data, the pointer guint8 *data is accessed without validation, resulting in a null pointer dereference. This vulnerability can result in a Denial of Service (DoS) by triggering a segmentation fault (SEGV). This vulnerability is fixed in 1.24.10.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47542
