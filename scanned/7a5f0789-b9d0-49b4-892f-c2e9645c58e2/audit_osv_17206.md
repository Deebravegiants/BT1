# [H] CVE-2020-13695

## Summary
Severity: High
Advisory: CVE-2020-13695
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-01
Source: https://osv.dev/vulnerability/CVE-2020-13695
Type: osv

## Details
In QuickBox Community Edition through 2.5.5 and Pro Edition through 2.1.8, the local www-data user has sudo privileges to execute grep as root without a password, which allows an attacker to obtain sensitive information via a grep of a /root/*.db or /etc/shadow file.

## References
- https://s1gh.sh/cve-2020-13448-quickbox-authenticated-rce/
