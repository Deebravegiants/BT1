# [C] ALPINE-CVE-2016-7411

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7411
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7411
Type: osv

## Affected
- Alpine:v3.2: `php` — affected >=0 <5.6.27-r0
- Alpine:v3.3: `php` — affected >=0 <5.6.27-r0

## Details
ext/standard/var_unserializer.re in PHP before 5.6.26 mishandles object-deserialization failures, which allows remote attackers to cause a denial of service (memory corruption) or possibly have unspecified other impact via an unserialize call that references a partially constructed object.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7411
