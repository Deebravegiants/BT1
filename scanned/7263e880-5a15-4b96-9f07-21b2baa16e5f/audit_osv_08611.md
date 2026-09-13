# [M] CVE-2016-4804

## Summary
Severity: Medium
Advisory: CVE-2016-4804
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-03
Source: https://osv.dev/vulnerability/CVE-2016-4804
Type: osv

## Details
The read_boot function in boot.c in dosfstools before 4.0 allows attackers to cause a denial of service (crash) via a crafted filesystem, which triggers a heap-based buffer overflow in the (1) read_fat function or an out-of-bounds heap read in (2) get_fat function.

## References
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00001.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00014.html
- http://www.securityfocus.com/bid/90311
- https://lists.debian.org/debian-lts-announce/2020/05/msg00028.html
- http://www.ubuntu.com/usn/USN-2986-1
- https://blog.fuzzing-project.org/44-dosfstools-fsck.vfat-Several-invalid-memory-accesses.html
- https://github.com/dosfstools/dosfstools/commit/e8eff147e9da1185f9afd5b25948153a3b97cf52
- https://github.com/dosfstools/dosfstools/issues/25
- https://github.com/dosfstools/dosfstools/issues/26
