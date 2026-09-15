# [M] CVE-2017-16804

## Summary
Severity: Medium
Advisory: CVE-2017-16804
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2017-16804
Type: osv

## Details
In Redmine before 3.2.7 and 3.3.x before 3.3.4, the reminders function in app/models/mailer.rb does not check whether an issue is visible, which allows remote authenticated users to obtain sensitive information by reading e-mail reminder messages.

## References
- https://www.debian.org/security/2018/dsa-4191
- https://www.redmine.org/issues/25713
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://github.com/redmine/redmine/commit/0f09f161f64f4190a52166675ff380a15b72a8bc
