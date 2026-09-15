# [H] ALPINE-CVE-2021-36770

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-36770
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-36770
Type: osv

## Affected
- Alpine:v3.15: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.16: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.17: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.18: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.19: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.20: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.21: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.22: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.23: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.24: `perl` — affected >=0 <5.34.0-r1
- Alpine:v3.15: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.16: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.17: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.18: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.19: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.20: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.21: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.22: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.23: `perl-encode` — affected >=0 <3.12-r0
- Alpine:v3.24: `perl-encode` — affected >=0 <3.12-r0

## Details
Encode.pm, as distributed in Perl through 5.34.0, allows local users to gain privileges via a Trojan horse Encode::ConfigLocal library (in the current working directory) that preempts dynamic module loading. Exploitation requires an unusual configuration, and certain 2021 versions of Encode.pm (3.05 through 3.11). This issue occurs because the || operator evaluates @INC in a scalar context, and thus @INC has only an integer value.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-36770
