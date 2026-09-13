# [C] ALPINE-CVE-2018-7225

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-7225
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7225
Type: osv

## Affected
- Alpine:v3.10: `libvncserver` — affected >=0 <0.9.11-r2
- Alpine:v3.11: `libvncserver` — affected >=0 <0.9.11-r2
- Alpine:v3.5: `libvncserver` — affected >=0 <0.9.11-r1
- Alpine:v3.6: `libvncserver` — affected >=0 <0.9.11-r1
- Alpine:v3.7: `libvncserver` — affected >=0 <0.9.11-r2
- Alpine:v3.8: `libvncserver` — affected >=0 <0.9.11-r2
- Alpine:v3.9: `libvncserver` — affected >=0 <0.9.11-r2

## Details
An issue was discovered in LibVNCServer through 0.9.11. rfbProcessClientNormalMessage() in rfbserver.c does not sanitize msg.cct.length, leading to access to uninitialized and potentially sensitive data or possibly unspecified other impact (e.g., an integer overflow) via specially crafted VNC packets.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7225
