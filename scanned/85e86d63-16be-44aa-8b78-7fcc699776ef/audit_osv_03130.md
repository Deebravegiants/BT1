# [C] ALPINE-CVE-2024-47607

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-47607
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47607
Type: osv

## Affected
- Alpine:v3.20: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.21: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.22: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.23: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.24: `gst-plugins-base` — affected >=0 <1.24.10-r0

## Details
GStreamer is a library for constructing graphs of media-handling components.  stack-buffer overflow has been detected in the gst_opus_dec_parse_header function within `gstopusdec.c'. The pos array is a stack-allocated buffer of size 64. If n_channels exceeds 64, the for loop will write beyond the boundaries of the pos array. The value written will always be GST_AUDIO_CHANNEL_POSITION_NONE. This bug allows to overwrite the EIP address allocated in the stack. This vulnerability is fixed in 1.24.10.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47607
