# [M] CVE-2018-18521

## Summary
Severity: Medium
Advisory: CVE-2018-18521
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-19
Source: https://osv.dev/vulnerability/CVE-2018-18521
Type: osv

## Details
Divide-by-zero vulnerabilities in the function arlib_add_symbols() in arlib.c in elfutils 0.174 allow remote attackers to cause a denial of service (application crash) with a crafted ELF file, as demonstrated by eu-ranlib, because a zero sh_entsize is mishandled.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- https://access.redhat.com/errata/RHSA-2019:2197
- https://lists.debian.org/debian-lts-announce/2019/02/msg00036.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00030.html
- https://usn.ubuntu.com/4012-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23786
- https://sourceware.org/ml/elfutils-devel/2018-q4/msg00055.html
