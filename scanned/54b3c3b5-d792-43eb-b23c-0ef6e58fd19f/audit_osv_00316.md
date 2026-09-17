# [M] ALPINE-CVE-2016-9813

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-9813
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9813
Type: osv

## Affected
- Alpine:v3.4: `gst-plugins-bad1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-bad1` — affected >=0 <1.8.3-r0

## Details
The _parse_pat function in the mpegts parser in GStreamer before 1.10.2 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9813
