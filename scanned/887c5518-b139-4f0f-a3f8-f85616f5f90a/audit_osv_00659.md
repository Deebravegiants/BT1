# [M] ALPINE-CVE-2017-5462

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-5462
Ecosystem: Alpine:v3.3, Alpine:v3.4
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5462
Type: osv

## Affected
- Alpine:v3.3: `nss` — affected >=0 <3.23-r1
- Alpine:v3.4: `nss` — affected >=0 <3.23-r1

## Details
A flaw in DRBG number generation within the Network Security Services (NSS) library where the internal state V does not correctly carry bits over. The NSS library has been updated to fix this issue to address this issue and Firefox ESR 52.1 has been updated with NSS version 3.28.4. This vulnerability affects Thunderbird < 52.1, Firefox ESR < 45.9, Firefox ESR < 52.1, and Firefox < 53.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5462
