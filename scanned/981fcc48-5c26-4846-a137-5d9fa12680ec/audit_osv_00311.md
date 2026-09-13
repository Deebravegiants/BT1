# [C] ALPINE-CVE-2016-9635

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-9635
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9635
Type: osv

## Affected
- Alpine:v3.7: `gst-plugins-good` — affected >=0 <1.10.4-r0
- Alpine:v3.4: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.6: `gst-plugins-good1` — affected >=0 <1.10.4-r0

## Details
Heap-based buffer overflow in the flx_decode_delta_fli function in gst/flx/gstflxdec.c in the FLIC decoder in GStreamer before 1.10.2 allows remote attackers to execute arbitrary code or cause a denial of service (application crash) by providing a 'skip count' that goes beyond initialized buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9635
