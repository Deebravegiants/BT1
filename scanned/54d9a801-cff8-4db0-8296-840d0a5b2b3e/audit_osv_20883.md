# [H] CVE-2021-38084

## Summary
Severity: High
Advisory: CVE-2021-38084
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-03
Source: https://osv.dev/vulnerability/CVE-2021-38084
Type: osv

## Details
An issue was discovered in the POP3 component of Courier Mail Server before 1.1.5. Meddler-in-the-middle attackers can pipeline commands after the POP3 STLS command, injecting plaintext commands into an encrypted user session.

## References
- https://sourceforge.net/p/courier/mailman/courier-imap/thread/cone.1382574216.483027.8082.1000%40monster.email-scan.com/#msg31555583
- https://sourceforge.net/p/courier/mailman/message/37329216/
