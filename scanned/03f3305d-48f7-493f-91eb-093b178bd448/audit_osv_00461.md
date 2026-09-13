# [H] ALPINE-CVE-2017-13090

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-13090
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13090
Type: osv

## Affected
- Alpine:v3.10: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.11: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.12: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.13: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.14: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.15: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.16: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.17: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.18: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.19: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.20: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.21: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.22: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.23: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.24: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.4: `wget` — affected >=0 <1.18-r2
- Alpine:v3.5: `wget` — affected >=0 <1.18-r3
- Alpine:v3.6: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.7: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.8: `wget` — affected >=0 <1.19.2-r0
- Alpine:v3.9: `wget` — affected >=0 <1.19.2-r0

## Details
The retr.c:fd_read_body() function is called when processing OK responses. When the response is sent chunked in wget before 1.19.2, the chunk parser uses strtol() to read each chunk's length, but doesn't check that the chunk length is a non-negative number. The code then tries to read the chunk in pieces of 8192 bytes by using the MIN() macro, but ends up passing the negative chunk length to retr.c:fd_read(). As fd_read() takes an int argument, the high 32 bits of the chunk length are discarded, leaving fd_read() with a completely attacker controlled length argument. The attacker can corrupt malloc metadata after the allocated buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13090
