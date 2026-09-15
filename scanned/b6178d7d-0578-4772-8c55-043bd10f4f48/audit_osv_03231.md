# [M] ALPINE-CVE-2025-26465

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-26465
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-26465
Type: osv

## Affected
- Alpine:v3.18: `openssh` — affected >=6.9 <9.3_p2-r3
- Alpine:v3.19: `openssh` — affected >=6.9 <9.6_p1-r2
- Alpine:v3.20: `openssh` — affected >=6.9 <9.7_p1-r5
- Alpine:v3.21: `openssh` — affected >=6.9 <9.9_p2-r0
- Alpine:v3.22: `openssh` — affected >=6.9 <9.9_p2-r0
- Alpine:v3.23: `openssh` — affected >=6.9 <9.9_p2-r0
- Alpine:v3.24: `openssh` — affected >=6.9 <9.9_p2-r0

## Details
A vulnerability was found in OpenSSH when the VerifyHostKeyDNS option is enabled. A machine-in-the-middle attack can be performed by a malicious machine impersonating a legit server. This issue occurs due to how OpenSSH mishandles error codes in specific conditions when verifying the host key. For an attack to be considered successful, the attacker needs to manage to exhaust the client's memory resource first, turning the attack complexity high.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-26465
