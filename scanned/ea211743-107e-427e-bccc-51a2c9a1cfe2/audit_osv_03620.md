# [C] ALPINE-CVE-2026-34235

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-34235
Ecosystem: Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34235
Type: osv

## Affected
- Alpine:v3.24: `pjproject` — affected >=0 <2.17-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. Prior to version 2.17, a heap out-of-bounds read vulnerability exists in PJSIP's VP9 RTP unpacketizer that occurs when parsing crafted VP9 Scalability Structure (SS) data. Insufficient bounds checking on the payload descriptor length may cause reads beyond the allocated RTP payload buffer. This issue has been patched in version 2.17. A workaround for this issue involves disabling VP9 codec if not needed.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34235
