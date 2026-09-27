# [M] CVE-2017-7612

## Summary
Severity: Medium
Advisory: CVE-2017-7612
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7612
Type: osv

## Details
The check_sysv_hash function in elflint.c in elfutils 0.168 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://lists.debian.org/debian-lts-announce/2019/02/msg00036.html
- https://security.gentoo.org/glsa/201710-10
- https://usn.ubuntu.com/3670-1/
- https://blogs.gentoo.org/ago/2017/04/03/elfutils-heap-based-buffer-overflow-in-check_sysv_hash-elflint-c
