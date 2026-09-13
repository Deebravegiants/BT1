# [H] CVE-2017-7413

## Summary
Severity: High
Advisory: CVE-2017-7413
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-04
Source: https://osv.dev/vulnerability/CVE-2017-7413
Type: osv

## Details
In Horde_Crypt before 2.7.6, as used in Horde Groupware Webmail Edition through 5.2.17, OS Command Injection can occur if the attacker is an authenticated Horde Webmail user, has PGP features enabled in their preferences, and attempts to encrypt an email addressed to a maliciously crafted email address.

## References
- https://lists.debian.org/debian-lts-announce/2018/06/msg00006.html
- https://lists.horde.org/archives/horde/Week-of-Mon-20170403/056767.html
