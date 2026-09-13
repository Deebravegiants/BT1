# [M] ALPINE-CVE-2019-15961

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-15961
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15961
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.100.5-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.102.0-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.102.0-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.102.0-r0

## Details
A vulnerability in the email parsing module Clam AntiVirus (ClamAV) Software versions 0.102.0, 0.101.4 and prior could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to inefficient MIME parsing routines that result in extremely long scan times of specially formatted email files. An attacker could exploit this vulnerability by sending a crafted email file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process to scan the crafted email file indefinitely, resulting in a denial of service condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15961
