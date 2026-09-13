# [H] ALPINE-CVE-2020-25648

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25648
Ecosystem: Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25648
Type: osv

## Affected
- Alpine:v3.12: `nss` — affected >=0 <3.58-r0
- Alpine:v3.19: `nss` — affected >=0 <3.58-r0
- Alpine:v3.20: `nss` — affected >=0 <3.58-r0
- Alpine:v3.21: `nss` — affected >=0 <3.58-r0
- Alpine:v3.22: `nss` — affected >=0 <3.58-r0
- Alpine:v3.23: `nss` — affected >=0 <3.58-r0
- Alpine:v3.24: `nss` — affected >=0 <3.58-r0

## Details
A flaw was found in the way NSS handled CCS (ChangeCipherSpec) messages in TLS 1.3. This flaw allows a remote attacker to send multiple CCS messages, causing a denial of service for servers compiled with the NSS library. The highest threat from this vulnerability is to system availability. This flaw affects NSS versions before 3.58.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25648
