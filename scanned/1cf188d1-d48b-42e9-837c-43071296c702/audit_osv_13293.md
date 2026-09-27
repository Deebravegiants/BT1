# [M] CVE-2018-19129

## Summary
Severity: Medium
Advisory: CVE-2018-19129
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-09
Source: https://osv.dev/vulnerability/CVE-2018-19129
Type: osv

## Details
In Libav 12.3, a NULL pointer dereference (RIP points to zero) issue in ff_mpa_synth_filter_float in libavcodec/mpegaudiodsp_template.c can cause a segmentation fault (application crash) via a crafted mov file.

## References
- https://bugzilla.libav.org/show_bug.cgi?id=1138
