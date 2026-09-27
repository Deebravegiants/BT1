# [C] GHSL-2024-115: GStreamer has a stack-buffer overflow in vorbis_handle_identification_packet

## Summary
Severity: Critical
Advisory: CVE-2024-47538
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-47538
Type: osv

## Details
GStreamer is a library for constructing graphs of media-handling components. A stack-buffer overflow has been detected in the `vorbis_handle_identification_packet` function within `gstvorbisdec.c`. The position array is a stack-allocated buffer of size 64. If vd->vi.channels exceeds 64, the for loop will write beyond the boundaries of the position array. The value written will always be `GST_AUDIO_CHANNEL_POSITION_NONE`. This vulnerability allows someone to overwrite the EIP address allocated in the stack. Additionally, this bug can overwrite the `GstAudioInfo` info structure. This vulnerability is fixed in 1.24.10.

## References
- https://gstreamer.freedesktop.org/security/sa-2024-0022.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00021.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47538.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47538
- https://securitylab.github.com/advisories/GHSL-2024-115_GHSL-2024-118_Gstreamer/
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/8035.patch
