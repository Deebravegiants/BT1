# [M] CVE-2021-38373

## Summary
Severity: Medium
Advisory: CVE-2021-38373
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-10
Source: https://osv.dev/vulnerability/CVE-2021-38373
Type: osv

## Details
In KDE KMail 19.12.3 (aka 5.13.3), the SMTP STARTTLS option is not honored (and cleartext messages are sent) unless "Server requires authentication" is checked.

## References
- https://bugs.kde.org/show_bug.cgi?id=423423
- https://nostarttls.secvuln.info
