# [M] ALPINE-CVE-2023-6129

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-6129
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-01-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-6129
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.12-r2
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.1.4-r3
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.1.4-r3
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.1.4-r3
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.1.4-r3
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.1.4-r3
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.1.4-r3
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.1.4-r3

## Details
Issue summary: The POLY1305 MAC (message authentication code) implementation
contains a bug that might corrupt the internal state of applications running
on PowerPC CPU based platforms if the CPU provides vector instructions.

Impact summary: If an attacker can influence whether the POLY1305 MAC
algorithm is used, the application state might be corrupted with various
application dependent consequences.

The POLY1305 MAC (message authentication code) implementation in OpenSSL for
PowerPC CPUs restores the contents of vector registers in a different order
than they are saved. Thus the contents of some of these vector registers
are corrupted when returning to the caller. The vulnerable code is used only
on newer PowerPC processors supporting the PowerISA 2.07 instructions.

The consequences of this kind of internal application state corruption can
be various - from no consequences, if the calling application does not
depend on the contents of non-volatile XMM registers at all, to the worst
consequences, where the attacker could get complete control of the application
process. However unless the compiler uses the vector registers for storing
pointers, the most likely consequence, if any, would be an incorrect result
of some application dependent calculations or a crash leading to a denial of
service.

The POLY1305 MAC algorithm is most frequently used as part of the
CHACHA20-POLY1305 AEAD (authenticated encryption with associated data)
algorithm. The most common usage of this AEAD cipher is with TLS protocol
versions 1.2 and 1.3. If this cipher is enabled on the server a malicious
client can influence whether this AEAD cipher is used. This implies that
TLS server applications using OpenSSL can be potentially impacted. However
we are currently not aware of any concrete application that would be affected
by this issue therefore we consider this a Low severity security issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-6129
