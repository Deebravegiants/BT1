# [M] ALPINE-CVE-2020-15260

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-15260
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15260
Type: osv

## Affected
- Alpine:v3.14: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.15: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.16: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.17: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.18: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.11-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.11-r0

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In version 2.10 and earlier, PJSIP transport can be reused if they have the same IP address + port + protocol. However, this is insufficient for secure transport since it lacks remote hostname authentication. Suppose we have created a TLS connection to `sip.foo.com`, which has an IP address `100.1.1.1`. If we want to create a TLS connection to another hostname, say `sip.bar.com`, which has the same IP address, then it will reuse that existing connection, even though `100.1.1.1` does not have certificate to authenticate as `sip.bar.com`. The vulnerability allows for an insecure interaction without user awareness. It affects users who need access to connections to different destinations that translate to the same address, and allows man-in-the-middle attack if attacker can route a connection to another destination such as in the case of DNS spoofing.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15260
