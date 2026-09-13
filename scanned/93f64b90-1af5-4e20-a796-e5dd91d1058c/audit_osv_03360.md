# [M] ALPINE-CVE-2025-59801

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-59801
Ecosystem: Alpine:v3.23
CVSS: 4.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-59801
Type: osv

## Affected
- Alpine:v3.23: `ghostscript` — affected >=0 <10.06.0-r0

## Details
In Artifex GhostXPS before 10.06.0, there is a stack-based buffer overflow in xps_unpredict_tiff in xpstiff.c because the samplesperpixel value is not checked.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-59801
