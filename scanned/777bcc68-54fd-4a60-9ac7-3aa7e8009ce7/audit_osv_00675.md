# [H] ALPINE-CVE-2017-5839

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5839
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5839
Type: osv

## Affected
- Alpine:v3.4: `gst-plugins-base1` — affected >=0 <1.8.3-r0
- Alpine:v3.5: `gst-plugins-base1` — affected >=0 <1.8.3-r0

## Details
The gst_riff_create_audio_caps function in gst-libs/gst/riff/riff-media.c in gst-plugins-base in GStreamer before 1.10.3 does not properly limit recursion, which allows remote attackers to cause a denial of service (stack overflow and crash) via vectors involving nested WAVEFORMATEX.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5839
