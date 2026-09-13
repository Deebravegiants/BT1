# [H] ALPINE-CVE-2017-12374

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12374
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12374
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.99.3-r0

## Details
The ClamAV AntiVirus software versions 0.99.2 and prior contain a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to a lack of input validation checking mechanisms during certain mail parsing operations (mbox.c operations on bounce messages). If successfully exploited, the ClamAV software could allow a variable pointing to the mail body which could cause a used after being free (use-after-free) instance which may lead to a disruption of services on an affected device to include a denial of service condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12374
