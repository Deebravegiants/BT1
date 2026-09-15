# [M] CVE-2019-14466

## Summary
Severity: Medium
Advisory: CVE-2019-14466
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-12-31
Source: https://osv.dev/vulnerability/CVE-2019-14466
Type: osv

## Details
The GOsa_Filter_Settings cookie in GONICUS GOsa 2.7.5.2 is vulnerable to PHP objection injection, which allows a remote authenticated attacker to perform file deletions (in the context of the user account that runs the web server) via a crafted cookie value, because unserialize is used to restore filter settings from a cookie.

## References
- https://lists.debian.org/debian-lts-announce/2019/08/msg00039.html
- https://github.com/gosa-project/gosa-core/pull/29
