# [H] ALPINE-CVE-2016-9808

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9808
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9808
Type: osv

## Affected
- Alpine:v3.7: `gst-plugins-good` — affected >=0 <1.10.4-r0
- Alpine:v3.4: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-good1` — affected >=0 <1.8.3-r0
- Alpine:v3.6: `gst-plugins-good1` — affected >=0 <1.10.4-r0

## Details
The FLIC decoder in GStreamer before 1.10.2 allows remote attackers to cause a denial of service (out-of-bounds write and crash) via a crafted series of skip and count pairs.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9808
