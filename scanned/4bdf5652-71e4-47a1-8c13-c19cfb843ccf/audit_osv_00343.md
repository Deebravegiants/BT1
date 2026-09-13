# [C] ALPINE-CVE-2016-9941

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-9941
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9941
Type: osv

## Affected
- Alpine:v3.10: `libvncserver` — affected >=0 <0.9.11-r0
- Alpine:v3.11: `libvncserver` — affected >=0 <0.9.11-r0
- Alpine:v3.2: `libvncserver` — affected >=0 <0.9.10-r2
- Alpine:v3.3: `libvncserver` — affected >=0 <0.9.10-r2
- Alpine:v3.4: `libvncserver` — affected >=0 <0.9.10-r2
- Alpine:v3.5: `libvncserver` — affected >=0 <0.9.10-r2
- Alpine:v3.6: `libvncserver` — affected >=0 <0.9.11-r0
- Alpine:v3.7: `libvncserver` — affected >=0 <0.9.11-r0
- Alpine:v3.8: `libvncserver` — affected >=0 <0.9.11-r0
- Alpine:v3.9: `libvncserver` — affected >=0 <0.9.11-r0

## Details
Heap-based buffer overflow in rfbproto.c in LibVNCClient in LibVNCServer before 0.9.11 allows remote servers to cause a denial of service (application crash) or possibly execute arbitrary code via a crafted FramebufferUpdate message containing a subrectangle outside of the client drawing area.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9941
