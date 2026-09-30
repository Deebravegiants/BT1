# [H] ALPINE-CVE-2018-10536

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-10536
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10536
Type: osv

## Affected
- Alpine:v3.10: `wavpack` — affected >=0 <5.1.0-r6
- Alpine:v3.11: `wavpack` — affected >=0 <5.1.0-r6
- Alpine:v3.4: `wavpack` — affected >=0 <5.1.0-r2
- Alpine:v3.5: `wavpack` — affected >=0 <5.1.0-r2
- Alpine:v3.6: `wavpack` — affected >=0 <5.1.0-r2
- Alpine:v3.7: `wavpack` — affected >=0 <5.1.0-r2
- Alpine:v3.8: `wavpack` — affected >=0 <5.1.0-r6
- Alpine:v3.9: `wavpack` — affected >=0 <5.1.0-r6

## Details
An issue was discovered in WavPack 5.1.0 and earlier. The WAV parser component contains a vulnerability that allows writing to memory because ParseRiffHeaderConfig in riff.c does not reject multiple format chunks.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10536
