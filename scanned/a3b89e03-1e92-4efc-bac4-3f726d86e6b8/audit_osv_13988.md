# [M] CVE-2018-6182

## Summary
Severity: Medium
Advisory: CVE-2018-6182
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-04-09
Source: https://osv.dev/vulnerability/CVE-2018-6182
Type: osv

## Details
Mahara 16.10 before 16.10.9 and 17.04 before 17.04.7 and 17.10 before 17.10.4 are vulnerable to bad input when TinyMCE is bypassed by POST packages. Therefore, Mahara should not rely on TinyMCE's code stripping alone but also clean input on the server / PHP side as one can create own packets of POST data containing bad content with which to hit the server.

## References
- https://mahara.org/interaction/forum/topic.php?id=8215
- https://bugs.launchpad.net/mahara/+bug/1744789
