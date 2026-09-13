# [M] ALPINE-CVE-2017-3736

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3736
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3736
Type: osv

## Affected
- Alpine:v3.3: `openssl` — affected >=1.0.2 <1.0.2m-r0
- Alpine:v3.4: `openssl` — affected >=1.0.2 <1.0.2m-r0
- Alpine:v3.5: `openssl` — affected >=1.0.2 <1.0.2m-r0
- Alpine:v3.6: `openssl` — affected >=1.0.2 <1.0.2m-r0
- Alpine:v3.7: `openssl` — affected >=1.0.2 <1.0.2m-r0
- Alpine:v3.8: `openssl` — affected >=1.0.2 <1.0.2m-r0

## Details
There is a carry propagating bug in the x86_64 Montgomery squaring procedure in OpenSSL before 1.0.2m and 1.1.0 before 1.1.0g. No EC algorithms are affected. Analysis suggests that attacks against RSA and DSA as a result of this defect would be very difficult to perform and are not believed likely. Attacks against DH are considered just feasible (although very difficult) because most of the work necessary to deduce information about a private key may be performed offline. The amount of resources required for such an attack would be very significant and likely only accessible to a limited number of attackers. An attacker would additionally need online access to an unpatched system using the target private key in a scenario with persistent DH parameters and a private key that is shared between multiple clients. This only affects processors that support the BMI1, BMI2 and ADX extensions like Intel Broadwell (5th generation) and later or AMD Ryzen.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3736
