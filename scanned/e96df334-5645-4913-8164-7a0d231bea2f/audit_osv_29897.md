# [C] GHSL-2024-116: Stack-buffer overflow in gst_opus_dec_parse_header

## Summary
Severity: Critical
Advisory: CVE-2024-47607
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47607
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components.  stack-buffer overflow has been detected in the gst_opus_dec_parse_header function within `gstopusdec.c'. The pos array is a stack-allocated buffer of size 64. If n_channels exceeds 64, the for loop will write beyond the boundaries of the pos array. The value written will always be GST_AUDIO_CHANNEL_POSITION_NONE. This bug allows to overwrite the EIP address allocated in the stack. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0024.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00021.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47607.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47607
- https://securitylab.github.com/advisories/GHSL-2024-115_GHSL-2024-118_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8037.patch
