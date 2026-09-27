# [C] ALPINE-CVE-2017-5461

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-5461
Ecosystem: Alpine:v3.3, Alpine:v3.4
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5461
Type: osv

## Affected
- Alpine:v3.3: `nss` — affected >=0 <3.23-r1
- Alpine:v3.4: `nss` — affected >=0 <3.23-r1

## Details
Mozilla Network Security Services (NSS) before 3.21.4, 3.22.x through 3.28.x before 3.28.4, 3.29.x before 3.29.5, and 3.30.x before 3.30.1 allows remote attackers to cause a denial of service (out-of-bounds write) or possibly have unspecified other impact by leveraging incorrect base64 operations.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5461
