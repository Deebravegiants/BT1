# [C] ALPINE-CVE-2016-10033

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-10033
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10033
Type: osv

## Affected
- Alpine:v3.2: `php-phpmailer` — affected >=0 <5.2.4-r0
- Alpine:v3.3: `php-phpmailer` — affected >=0 <5.2.4-r0
- Alpine:v3.4: `php5-phpmailer` — affected >=0 <5.2.0-r1
- Alpine:v3.5: `php5-phpmailer` — affected >=0 <5.2.4-r1

## Details
The mailSend function in the isMail transport in PHPMailer before 5.2.18 might allow remote attackers to pass extra parameters to the mail command and consequently execute arbitrary code via a \" (backslash double quote) in a crafted Sender property.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10033
