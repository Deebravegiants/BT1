# [M] CVE-2023-45913

## Summary
Severity: Medium
Advisory: CVE-2023-45913
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-45913
Type: osv

## Details
Mesa v23.0.4 was discovered to contain a NULL pointer dereference via the function dri2GetGlxDrawableFromXDrawableId(). This vulnerability is triggered when the X11 server sends an DRI2_BufferSwapComplete event unexpectedly when the application is using DRI3. NOTE: this is disputed because there is no scenario in which the vulnerability was demonstrated.

## References
- http://packetstormsecurity.com/files/176800/Mesa-23.0.4-Null-Pointer.html
- http://seclists.org/fulldisclosure/2024/Jan/28
- https://seclists.org/fulldisclosure/2024/Jan/71
- https://gitlab.freedesktop.org/mesa/mesa/-/issues/9856
