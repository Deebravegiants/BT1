# [M] ALPINE-CVE-2016-7055

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-7055
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7055
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=1.0.2 <1.0.2k-r0
- Alpine:v3.3: `openssl` — affected >=1.0.2 <1.0.2k-r0
- Alpine:v3.4: `openssl` — affected >=1.0.2 <1.0.2k-r0

## Details
There is a carry propagating bug in the Broadwell-specific Montgomery multiplication procedure in OpenSSL 1.0.2 and 1.1.0 before 1.1.0c that handles input lengths divisible by, but longer than 256 bits. Analysis suggests that attacks against RSA, DSA and DH private keys are impossible. This is because the subroutine in question is not used in operations with the private key itself and an input of the attacker's direct choice. Otherwise the bug can manifest itself as transient authentication and key negotiation failures or reproducible erroneous outcome of public-key operations with specially crafted input. Among EC algorithms only Brainpool P-512 curves are affected and one presumably can attack ECDH key negotiation. Impact was not analyzed in detail, because pre-requisites for attack are considered unlikely. Namely multiple clients have to choose the curve in question and the server has to share the private key among them, neither of which is default behaviour. Even then only clients that chose the curve will be affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7055
