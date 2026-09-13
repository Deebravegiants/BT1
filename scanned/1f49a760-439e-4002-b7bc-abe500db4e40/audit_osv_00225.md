# [H] ALPINE-CVE-2016-7418

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7418
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7418
Type: osv

## Affected
- Alpine:v3.2: `php` — affected >=0 <5.6.27-r0
- Alpine:v3.3: `php` — affected >=0 <5.6.27-r0

## Details
The php_wddx_push_element function in ext/wddx/wddx.c in PHP before 5.6.26 and 7.x before 7.0.11 allows remote attackers to cause a denial of service (invalid pointer access and out-of-bounds read) or possibly have unspecified other impact via an incorrect boolean element in a wddxPacket XML document, leading to mishandling in a wddx_deserialize call.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7418
