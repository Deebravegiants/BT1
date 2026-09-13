# [C] ALPINE-CVE-2018-16395

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-16395
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16395
Type: osv

## Affected
- Alpine:v3.11: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.12: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.13: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.14: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.15: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.16: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.17: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.18: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.19: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.20: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.21: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.22: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.23: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.24: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.4: `ruby` — affected >=2.3.0 <2.3.8-r0
- Alpine:v3.5: `ruby` — affected >=2.3.0 <2.3.8-r0
- Alpine:v3.6: `ruby` — affected >=2.3.0 <2.4.5-r0
- Alpine:v3.7: `ruby` — affected >=2.3.0 <2.4.5-r0
- Alpine:v3.8: `ruby` — affected >=2.3.0 <2.5.2-r0
- Alpine:v3.9: `ruby` — affected >=2.3.0 <2.5.2-r0

## Details
An issue was discovered in the OpenSSL library in Ruby before 2.3.8, 2.4.x before 2.4.5, 2.5.x before 2.5.2, and 2.6.x before 2.6.0-preview3. When two OpenSSL::X509::Name objects are compared using ==, depending on the ordering, non-equal objects may return true. When the first argument is one character longer than the second, or the second argument contains a character that is one less than a character in the same position of the first argument, the result of == will be true. This could be leveraged to create an illegitimate certificate that may be accepted as legitimate and then used in signing or encryption operations.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16395
