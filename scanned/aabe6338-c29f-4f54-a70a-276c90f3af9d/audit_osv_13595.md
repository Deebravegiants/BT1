# [M] CVE-2018-20482

## Summary
Severity: Medium
Advisory: CVE-2018-20482
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/CVE-2018-20482
Type: osv

## Details
GNU Tar through 1.30, when --sparse is used, mishandles file shrinkage during read access, which allows local users to cause a denial of service (infinite read loop in sparse_dump_region in sparse.c) by modifying a file that is supposed to be archived by a different user's process (e.g., a system backup running as root).

## References
- http://lists.gnu.org/archive/html/bug-tar/2018-12/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00077.html
- http://www.securityfocus.com/bid/106354
- https://lists.debian.org/debian-lts-announce/2018/12/msg00023.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00025.html
- https://security.gentoo.org/glsa/201903-05
- http://git.savannah.gnu.org/cgit/tar.git/commit/?id=c15c42ccd1e2377945fd0414eca1a49294bff454
- https://twitter.com/thatcks/status/1076166645708668928
- https://utcc.utoronto.ca/~cks/space/blog/sysadmin/TarFindingTruncateBug
- https://news.ycombinator.com/item?id=18745431
