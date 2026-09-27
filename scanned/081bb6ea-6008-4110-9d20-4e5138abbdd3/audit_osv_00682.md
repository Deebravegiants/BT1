# [H] ALPINE-CVE-2017-5847

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5847
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5847
Type: osv

## Affected
- Alpine:v3.7: `gst-plugins-ugly` — affected >=0 <1.10.4-r0
- Alpine:v3.4: `gst-plugins-ugly1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-ugly1` — affected >=0 <1.8.3-r0
- Alpine:v3.6: `gst-plugins-ugly1` — affected >=0 <1.10.4-r0

## Details
The gst_asf_demux_process_ext_content_desc function in gst/asfdemux/gstasfdemux.c in gst-plugins-ugly in GStreamer allows remote attackers to cause a denial of service (out-of-bounds heap read) via vectors involving extended content descriptors.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5847
