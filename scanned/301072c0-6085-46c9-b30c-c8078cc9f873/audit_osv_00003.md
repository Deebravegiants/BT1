# [C] ALPINE-CVE-2012-6706

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2012-6706
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2012-6706
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.99.4-r0

## Details
A VMSF_DELTA memory corruption was discovered in unrar before 5.5.5, as used in Sophos Anti-Virus Threat Detection Engine before 3.37.2 and other products, that can lead to arbitrary code execution. An integer overflow can be caused in DataSize+CurChannel. The result is a negative value of the "DestPos" variable, which allows the attacker to write out of bounds when setting Mem[DestPos].

## References
- https://security.alpinelinux.org/vuln/CVE-2012-6706
