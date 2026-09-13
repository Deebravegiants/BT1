# [H] ALPINE-CVE-2026-33069

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-33069
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33069
Type: osv

## Affected
- Alpine:v3.24: `pjproject` — affected >=0 <2.17-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. Versions 2.16 and below have a cascading out-of-bounds heap read in pjsip_multipart_parse(). After boundary string matching, curptr is advanced past the delimiter without verifying it has not reached the buffer end. This allows 1-2 bytes of adjacent heap memory to be read. All applications that process incoming SIP messages with multipart bodies or SDP content are potentially affected. This issue is resolved in version 2.17.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33069
