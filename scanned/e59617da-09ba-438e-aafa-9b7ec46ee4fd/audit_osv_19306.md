# [M] CVE-2021-20113

## Summary
Severity: Medium
Advisory: CVE-2021-20113
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-20113
Type: osv

## Details
An exposure of sensitive information vulnerability exists in TCExam <= 14.8.1. If a password reset request was made for an email address that was not registered with a user then we would be presented with an ‘unknown email’ error. If an email is given that is registered with a user then this error will not appear. A malicious actor could abuse this to enumerate the email addresses of

## References
- https://www.tenable.com/security/research/tra-2021-32
