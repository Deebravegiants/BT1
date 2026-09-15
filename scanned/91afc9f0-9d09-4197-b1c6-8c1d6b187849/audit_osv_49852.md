# [H] CVE-2019-19920

## Summary
Severity: High
Advisory: CVE-2019-19920
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-22
Source: https://osv.dev/vulnerability/CVE-2019-19920
Type: osv

## Details
sa-exim 4.2.1 allows attackers to execute arbitrary code if they can write a .cf file or a rule. This occurs because Greylisting.pm relies on eval (rather than direct parsing and/or use of the taint feature). This issue is similar to CVE-2018-11805.

## References
- https://usn.ubuntu.com/4520-1/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00006.html
- https://marc.info/?l=spamassassin-users&m=157668107325768&w=2
- https://marc.info/?l=spamassassin-users&m=157668305026635&w=2
- https://bugs.debian.org/946829#24
