# [M] CVE-2017-7613

## Summary
Severity: Medium
Advisory: CVE-2017-7613
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7613
Type: osv

## Details
elflint.c in elfutils 0.168 does not validate the number of sections and the number of segments, which allows remote attackers to cause a denial of service (memory consumption) via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://lists.debian.org/debian-lts-announce/2019/02/msg00036.html
- https://security.gentoo.org/glsa/201710-10
- https://usn.ubuntu.com/3670-1/
- https://blogs.gentoo.org/ago/2017/04/03/elfutils-memory-allocation-failure-in-xcalloc-xmalloc-c
