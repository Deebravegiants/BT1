# [C] ALPINE-CVE-2016-7413

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7413
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7413
Type: osv

## Affected
- Alpine:v3.2: `php` — affected >=0 <5.6.27-r0
- Alpine:v3.3: `php` — affected >=0 <5.6.27-r0

## Details
Use-after-free vulnerability in the wddx_stack_destroy function in ext/wddx/wddx.c in PHP before 5.6.26 and 7.x before 7.0.11 allows remote attackers to cause a denial of service or possibly have unspecified other impact via a wddxPacket XML document that lacks an end-tag for a recordset field element, leading to mishandling in a wddx_deserialize call.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7413
