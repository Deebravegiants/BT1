# [H] ALPINE-CVE-2024-47835

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-47835
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47835
Type: osv

## Affected
- Alpine:v3.20: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.21: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.22: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.23: `gst-plugins-base` — affected >=0 <1.24.10-r0
- Alpine:v3.24: `gst-plugins-base` — affected >=0 <1.24.10-r0

## Details
GStreamer is a library for constructing graphs of media-handling components. A null pointer dereference vulnerability has been detected in the parse_lrc function within gstsubparse.c. The parse_lrc function calls strchr() to find the character ']' in the string line. The pointer returned by this call is then passed to g_strdup(). However, if the string line does not contain the character ']', strchr() returns NULL, and a call to g_strdup(start + 1) leads to a null pointer dereference. This vulnerability is fixed in 1.24.10.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47835
