# [H] ALPINE-CVE-2022-0934

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-0934
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0934
Type: osv

## Affected
- Alpine:v3.15: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.16: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.17: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.18: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.19: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.20: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.21: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.86-r1
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.86-r1

## Details
A single-byte, non-arbitrary write/use-after-free flaw was found in dnsmasq. This flaw allows an attacker who sends a crafted packet processed by dnsmasq, potentially causing a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0934
