# [M] ALPINE-CVE-2017-3732

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3732
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3732
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2k-r0
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2k-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2k-r0

## Details
There is a carry propagating bug in the x86_64 Montgomery squaring procedure in OpenSSL 1.0.2 before 1.0.2k and 1.1.0 before 1.1.0d. No EC algorithms are affected. Analysis suggests that attacks against RSA and DSA as a result of this defect would be very difficult to perform and are not believed likely. Attacks against DH are considered just feasible (although very difficult) because most of the work necessary to deduce information about a private key may be performed offline. The amount of resources required for such an attack would be very significant and likely only accessible to a limited number of attackers. An attacker would additionally need online access to an unpatched system using the target private key in a scenario with persistent DH parameters and a private key that is shared between multiple clients. For example this can occur by default in OpenSSL DHE based SSL/TLS ciphersuites. Note: This issue is very similar to CVE-2015-3193 but must be treated as a separate problem.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3732
