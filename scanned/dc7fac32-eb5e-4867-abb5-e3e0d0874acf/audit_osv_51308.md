# [H] CVE-2021-28374

## Summary
Severity: High
Advisory: CVE-2021-28374
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/CVE-2021-28374
Type: osv

## Details
The Debian courier-authlib package before 0.71.1-2 for Courier Authentication Library creates a /run/courier/authdaemon directory with weak permissions, allowing an attacker to read user information. This may include a cleartext password in some configurations. In general, it includes the user's existence, uid and gids, home and/or Maildir directory, quota, and some type of password information (such as a hash).

## References
- https://bugs.debian.org/984810
- https://lists.debian.org/debian-lts-announce/2021/04/msg00011.html
