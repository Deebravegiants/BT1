# [H] CVE-2019-13031

## Summary
Severity: High
Advisory: CVE-2019-13031
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-28
Source: https://osv.dev/vulnerability/CVE-2019-13031
Type: osv

## Details
LemonLDAP::NG before 1.9.20 has an XML External Entity (XXE) issue when submitting a notification to the notification server. By default, the notification server is not enabled and has a "deny all" rule.

## References
- https://lists.debian.org/debian-lts-announce/2019/07/msg00003.html
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/issues/1820
- https://www.calypt.com/blog/index.php/cve-2019-13031-xxe-on-lemonldapng-2-0-5/
