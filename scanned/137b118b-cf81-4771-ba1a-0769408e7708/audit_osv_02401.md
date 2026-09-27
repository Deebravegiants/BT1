# [H] ALPINE-CVE-2022-20698

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-20698
Ecosystem: Alpine:v3.12, Alpine:v3.13
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-20698
Type: osv

## Affected
- Alpine:v3.12: `clamav` — affected >=0.104.0 <0.103.6-r0
- Alpine:v3.13: `clamav` — affected >=0.104.0 <0.103.6-r0

## Details
A vulnerability in the OOXML parsing module in Clam AntiVirus (ClamAV) Software version 0.104.1 and LTS version 0.103.4 and prior versions could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to improper checks that may result in an invalid pointer read. An attacker could exploit this vulnerability by sending a crafted OOXML file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process to crash, resulting in a denial of service condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-20698
