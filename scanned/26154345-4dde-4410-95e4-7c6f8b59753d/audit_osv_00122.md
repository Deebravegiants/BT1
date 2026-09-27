# [H] ALPINE-CVE-2016-5129

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5129
Ecosystem: Alpine:v3.6
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-07-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5129
Type: osv

## Affected
- Alpine:v3.6: `nodejs` — affected >=0 <6.10.0-r0

## Details
Google V8 before 5.2.361.32, as used in Google Chrome before 52.0.2743.82, does not properly process left-trimmed objects, which allows remote attackers to cause a denial of service (memory corruption) or possibly have unspecified other impact via crafted JavaScript code.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5129
