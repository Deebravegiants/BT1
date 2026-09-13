# [M] ALPINE-CVE-2020-25683

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25683
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25683
Type: osv

## Affected
- Alpine:v3.10: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.11: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.12: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.13: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.14: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.15: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.16: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.17: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.18: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.19: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.20: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.21: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.83-r0

## Details
A flaw was found in dnsmasq before version 2.83. A heap-based buffer overflow was discovered in dnsmasq when DNSSEC is enabled and before it validates the received DNS entries. A remote attacker, who can create valid DNS replies, could use this flaw to cause an overflow in a heap-allocated memory. This flaw is caused by the lack of length checks in rfc1035.c:extract_name(), which could be abused to make the code execute memcpy() with a negative size in get_rdata() and cause a crash in dnsmasq, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25683
