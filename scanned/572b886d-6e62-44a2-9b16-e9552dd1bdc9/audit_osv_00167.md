# [C] ALPINE-CVE-2016-6354

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-6354
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6354
Type: osv

## Affected
- Alpine:v3.2: `flex` — affected >=0 <2.5.39-r1
- Alpine:v3.3: `flex` — affected >=0 <2.5.39-r3
- Alpine:v3.4: `flex` — affected >=0 <2.6.1-r0

## Details
Heap-based buffer overflow in the yy_get_next_buffer function in Flex before 2.6.1 might allow context-dependent attackers to cause a denial of service or possibly execute arbitrary code via vectors involving num_to_read.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6354
