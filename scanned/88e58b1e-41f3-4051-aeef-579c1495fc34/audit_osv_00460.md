# [H] ALPINE-CVE-2017-13089

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-13089
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13089
Type: osv

## Affected
- Alpine:v3.4: `wget` — affected >=0 <1.18-r2
- Alpine:v3.5: `wget` — affected >=0 <1.18-r3

## Details
The http.c:skip_short_body() function is called in some circumstances, such as when processing redirects. When the response is sent chunked in wget before 1.19.2, the chunk parser uses strtol() to read each chunk's length, but doesn't check that the chunk length is a non-negative number. The code then tries to skip the chunk in pieces of 512 bytes by using the MIN() macro, but ends up passing the negative chunk length to connect.c:fd_read(). As fd_read() takes an int argument, the high 32 bits of the chunk length are discarded, leaving fd_read() with a completely attacker controlled length argument.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13089
