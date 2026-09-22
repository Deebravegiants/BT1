# [C] ALPINE-CVE-2024-47600

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-47600
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47600
Type: osv

## Affected
- Alpine:v3.20: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.21: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.22: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.23: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.24: `gst-plugins-base` — affected >=0 <1.24.10-r0

## Details
GStreamer is a library for constructing graphs of media-handling components. An OOB-read vulnerability has been detected in the format_channel_mask function in gst-discoverer.c. The vulnerability affects the local array position, which is defined with a fixed size of 64 elements. However, the function gst_discoverer_audio_info_get_channels may return a guint channels value greater than 64. This causes the for loop to attempt access beyond the bounds of the position array, resulting in an OOB-read when an index greater than 63 is used. This vulnerability can result in reading unintended bytes from the stack. Additionally, the dereference of value->value_nick after the OOB-read can lead to further memory corruption or undefined behavior. This vulnerability is fixed in 1.24.10.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47600
