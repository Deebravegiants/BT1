# [M] ALPINE-CVE-2017-5842

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-5842
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5842
Type: osv

## Affected
- Alpine:v3.4: `gst-plugins-base1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-base1` — affected >=0 <1.8.3-r0

## Details
The html_context_handle_element function in gst/subparse/samiparse.c in gst-plugins-base in GStreamer before 1.10.3 allows remote attackers to cause a denial of service (out-of-bounds write) via a crafted SMI file, as demonstrated by OneNote_Manager.smi.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5842
