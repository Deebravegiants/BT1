# [M] ALPINE-CVE-2017-7526

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7526
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7526
Type: osv

## Affected
- Alpine:v3.10: `gnupg1` — affected >=0 <1.4.23-r0
- Alpine:v3.11: `gnupg1` — affected >=0 <1.4.23-r0
- Alpine:v3.12: `gnupg1` — affected >=0 <1.4.23-r0
- Alpine:v3.5: `gnupg1` — affected >=0 <1.4.23-r0
- Alpine:v3.6: `gnupg1` — affected >=0 <1.4.23-r0
- Alpine:v3.7: `gnupg1` — affected >=0 <1.4.23-r0
- Alpine:v3.8: `gnupg1` — affected >=0 <1.4.23-r0
- Alpine:v3.9: `gnupg1` — affected >=0 <1.4.23-r0

## Details
libgcrypt before version 1.7.8 is vulnerable to a cache side-channel attack resulting into a complete break of RSA-1024 while using the left-to-right method for computing the sliding-window expansion. The same attack is believed to work on RSA-2048 with moderately more computation. This side-channel requires that attacker can run arbitrary software on the hardware where the private RSA key is used.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7526
