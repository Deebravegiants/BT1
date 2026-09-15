# [C] ALPINE-CVE-2025-54874

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-54874
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-54874
Type: osv

## Affected
- Alpine:v3.21: `openjpeg` — affected >=0 <2.5.4-r0
- Alpine:v3.22: `openjpeg` — affected >=0 <2.5.4-r0
- Alpine:v3.23: `openjpeg` — affected >=0 <2.5.3-r1
- Alpine:v3.24: `openjpeg` — affected >=0 <2.5.3-r1

## Details
OpenJPEG is an open-source JPEG 2000 codec. In OpenJPEG from 2.5.1 through 2.5.3, a call to opj_jp2_read_header may lead to OOB heap memory write when the data stream p_stream is too short and p_image is not initialized.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-54874
