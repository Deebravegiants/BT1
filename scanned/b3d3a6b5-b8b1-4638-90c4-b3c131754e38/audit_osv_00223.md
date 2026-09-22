# [H] ALPINE-CVE-2016-7416

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7416
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7416
Type: osv

## Affected
- Alpine:v3.2: `php` — affected >=0 <5.6.27-r0
- Alpine:v3.3: `php` — affected >=0 <5.6.27-r0

## Details
ext/intl/msgformat/msgformat_format.c in PHP before 5.6.26 and 7.x before 7.0.11 does not properly restrict the locale length provided to the Locale class in the ICU library, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a MessageFormatter::formatMessage call with a long first argument.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7416
