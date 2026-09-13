# [H] CVE-2018-10195

## Summary
Severity: High
Advisory: CVE-2018-10195
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2018-10195
Type: osv

## Details
lrzsz before version 0.12.21~rc can leak information to the receiving side due to an incorrect length check in the function zsdata that causes a size_t to wrap around.

## References
- https://lists.suse.com/pipermail/sle-security-updates/2018-April/003955.html?_ga=2.81625751.1026327980.1622040648-1950393542.1547130931
- https://lists.suse.com/pipermail/sle-security-updates/2018-April/003956.html?_ga=2.81625751.1026327980.1622040648-1950393542.1547130931
- http://www.ohse.de/uwe/software/lrzsz.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1572058
- https://lists.debian.org/debian-lts-announce/2022/01/msg00027.html
