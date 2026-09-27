# [C] CVE-2023-45924

## Summary
Severity: Critical
Advisory: CVE-2023-45924
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-45924
Type: osv

## Details
libglxproto.c in OpenGL libglvnd bb06db5a was discovered to contain a segmentation violation via the function glXGetDrawableScreen(). NOTE: this is disputed because there are no common situations in which users require uninterrupted operation with an attacker-controller server.

## References
- http://seclists.org/fulldisclosure/2024/Jan/52
- http://packetstormsecurity.com/files/176807/libglvnd-bb06db5a-Buffer-Overflow-Null-Pointer.html
- https://gitlab.freedesktop.org/glvnd/libglvnd/-/issues/242
- https://gitlab.freedesktop.org/glvnd/libglvnd/-/merge_requests/295
