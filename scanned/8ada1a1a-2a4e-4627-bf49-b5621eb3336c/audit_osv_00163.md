# [M] ALPINE-CVE-2016-6313

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-6313
Ecosystem: Alpine:v3.4
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6313
Type: osv

## Affected
- Alpine:v3.4: `libgcrypt` — affected >=0 <1.7.0-r1

## Details
The mixing functions in the random number generator in Libgcrypt before 1.5.6, 1.6.x before 1.6.6, and 1.7.x before 1.7.3 and GnuPG before 1.4.21 make it easier for attackers to obtain the values of 160 bits by leveraging knowledge of the previous 4640 bits.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6313
