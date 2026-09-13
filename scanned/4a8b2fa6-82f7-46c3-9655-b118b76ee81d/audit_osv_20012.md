# [M] CVE-2021-29349

## Summary
Severity: Medium
Advisory: CVE-2021-29349
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-03-31
Source: https://osv.dev/vulnerability/CVE-2021-29349
Type: osv

## Details
Mahara 20.10 is affected by Cross Site Request Forgery (CSRF) that allows a remote attacker to remove inbox-mail on the server. The application fails to validate the CSRF token for a POST request. An attacker can craft a module/multirecipientnotification/inbox.php pieform_delete_all_notifications request, which leads to removing all messages from a mailbox.

## References
- https://github.com/0xBaz/CVE-2021-29349/issues/1
