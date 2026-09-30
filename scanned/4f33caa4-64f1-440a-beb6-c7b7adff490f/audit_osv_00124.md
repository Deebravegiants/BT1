# [C] ALPINE-CVE-2016-5180

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-5180
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5180
Type: osv

## Affected
- Alpine:v3.2: `c-ares` — affected >=0 <1.12.0-r0
- Alpine:v3.3: `c-ares` — affected >=0 <1.12.0-r0
- Alpine:v3.4: `c-ares` — affected >=0 <1.12.0-r0
- Alpine:v3.5: `c-ares` — affected >=0 <1.12.0-r0
- Alpine:v3.6: `c-ares` — affected >=0 <1.12.0-r0
- Alpine:v3.6: `nodejs` — affected >=0 <6.8.0-r0

## Details
Heap-based buffer overflow in the ares_create_query function in c-ares 1.x before 1.12.0 allows remote attackers to cause a denial of service (out-of-bounds write) or possibly execute arbitrary code via a hostname with an escaped trailing dot.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5180
