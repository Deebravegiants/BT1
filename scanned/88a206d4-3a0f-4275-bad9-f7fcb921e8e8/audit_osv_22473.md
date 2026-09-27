# [M] CVE-2022-30699

## Summary
Severity: Medium
Advisory: CVE-2022-30699
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-01
Source: https://osv.dev/vulnerability/CVE-2022-30699
Type: osv

## Details
NLnet Labs Unbound, up to and including version 1.16.1, is vulnerable to a novel type of the "ghost domain names" attack. The vulnerability works by targeting an Unbound instance. Unbound is queried for a rogue domain name when the cached delegation information is about to expire. The rogue nameserver delays the response so that the cached delegation information is expired. Upon receiving the delayed answer containing the delegation information, Unbound overwrites the now expired entries. This action can be repeated when the delegation information is about to expire making the rogue delegation information ever-updating. From version 1.16.2 on, Unbound stores the start time for a query and uses that to decide if the cached delegation information can be overwritten.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5L3ZFWZZFPBIL654BG75RWXUMPFQJ5EC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D35CX4SCZVNKZTWJXPDFTHWZHINMGEZD/
- https://security.gentoo.org/glsa/202212-02
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2022-30698_CVE-2022-30699.txt
