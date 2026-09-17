# [C] ALPINE-CVE-2024-47538

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-47538
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47538
Type: osv

## Affected
- Alpine:v3.20: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.21: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.22: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.23: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.24: `gst-plugins-base` — affected >=0 <1.24.10-r0

## Details
GStreamer is a library for constructing graphs of media-handling components. A stack-buffer overflow has been detected in the `vorbis_handle_identification_packet` function within `gstvorbisdec.c`. The position array is a stack-allocated buffer of size 64. If vd->vi.channels exceeds 64, the for loop will write beyond the boundaries of the position array. The value written will always be `GST_AUDIO_CHANNEL_POSITION_NONE`. This vulnerability allows someone to overwrite the EIP address allocated in the stack. Additionally, this bug can overwrite the `GstAudioInfo` info structure. This vulnerability is fixed in 1.24.10.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47538
