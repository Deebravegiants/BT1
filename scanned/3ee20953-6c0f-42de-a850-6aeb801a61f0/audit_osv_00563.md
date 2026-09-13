# [H] ALPINE-CVE-2017-16227

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-16227
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16227
Type: osv

## Affected
- Alpine:v3.3: `quagga` — affected >=0 <0.99.24.1-r6
- Alpine:v3.4: `quagga` — affected >=0 <1.0.20161017-r1
- Alpine:v3.5: `quagga` — affected >=0 <1.1.1-r1
- Alpine:v3.6: `quagga` — affected >=0 <1.2.2-r0

## Details
The aspath_put function in bgpd/bgp_aspath.c in Quagga before 1.2.2 allows remote attackers to cause a denial of service (session drop) via BGP UPDATE messages, because AS_PATH size calculation for long paths counts certain bytes twice and consequently constructs an invalid message.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16227
