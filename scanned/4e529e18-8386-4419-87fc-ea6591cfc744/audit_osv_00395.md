# [M] ALPINE-CVE-2017-11126

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-11126
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11126
Type: osv

## Affected
- Alpine:v3.3: `mpg123` — affected >=0 <1.25.4-r0
- Alpine:v3.4: `mpg123` — affected >=0 <1.25.4-r0
- Alpine:v3.5: `mpg123` — affected >=0 <1.25.4-r0
- Alpine:v3.6: `mpg123` — affected >=0 <1.25.4-r0

## Details
The III_i_stereo function in libmpg123/layer3.c in mpg123 through 1.25.1 allows remote attackers to cause a denial of service (buffer over-read and application crash) via a crafted audio file that is mishandled in the code for the "block_type != 2" case, a similar issue to CVE-2017-9870.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11126
