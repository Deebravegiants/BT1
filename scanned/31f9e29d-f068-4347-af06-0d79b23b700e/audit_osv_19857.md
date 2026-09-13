# [H] CVE-2021-26911

## Summary
Severity: High
Advisory: CVE-2021-26911
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/CVE-2021-26911
Type: osv

## Details
core/imap/MCIMAPSession.cpp in Canary Mail before 3.22 has Missing SSL Certificate Validation for IMAP in STARTTLS mode.

## References
- https://apps.apple.com/us/app/canary-mail/id1236045954
- https://census-labs.com/news/category/advisories/
- http://www.openwall.com/lists/oss-security/2021/02/17/3
- https://github.com/canarymail/mailcore2/commit/45acb4efbcaa57a20ac5127dc976538671fce018
- https://www.openwall.com/lists/oss-security/2021/02/17/3
- https://census-labs.com/news/2021/02/17/canary-mail-app-missing-certificate-validation-check-on-imap-starttls/
