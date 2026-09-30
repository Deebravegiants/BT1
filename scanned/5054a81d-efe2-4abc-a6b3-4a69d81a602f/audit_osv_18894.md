# [H] CVE-2020-36829

## Summary
Severity: High
Advisory: CVE-2020-36829
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2020-36829
Type: osv

## Details
The Mojolicious module before 8.65 for Perl is vulnerable to secure_compare timing attacks that allow an attacker to guess the length of a secret string. Only versions after 1.74 are affected.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00025.html
- https://github.com/mojolicious/mojo/issues/1599
- https://github.com/mojolicious/mojo/pull/1601
