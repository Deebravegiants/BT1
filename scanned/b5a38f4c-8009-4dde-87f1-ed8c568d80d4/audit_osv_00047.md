# [C] ALPINE-CVE-2016-10164

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-10164
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10164
Type: osv

## Affected
- Alpine:v3.2: `libxpm` — affected >=0 <3.5.12-r0
- Alpine:v3.3: `libxpm` — affected >=0 <3.5.12-r0
- Alpine:v3.4: `libxpm` — affected >=0 <3.5.12-r0

## Details
Multiple integer overflows in libXpm before 3.5.12, when a program requests parsing XPM extensions on a 64-bit platform, allow remote attackers to cause a denial of service (out-of-bounds write) or execute arbitrary code via (1) the number of extensions or (2) their concatenated length in a crafted XPM file, which triggers a heap-based buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10164
