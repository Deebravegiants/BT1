# [M] CVE-2021-3826

## Summary
Severity: Medium
Advisory: CVE-2021-3826
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2021-3826
Type: osv

## Details
Heap/stack buffer overflow in the dlang_lname function in d-demangle.c in libiberty allows attackers to potentially cause a denial of service (segmentation fault and crash) via a crafted mangled symbol.

## References
- https://gcc.gnu.org/git/?p=gcc.git%3Ba=commit%3Bh=5481040197402be6dfee265bd2ff5a4c88e30505
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4MYLS3VR4OPL5ECRWOR4ZHMGXUSCJFZY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6AKZ2DTS3ATVN5PANNVLKLE5OP4OF25Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MTEHT3G6YKJ7F7MSGWYSI4UM3XBAYXZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AXFC74WRZ2Q7F2TSUKPYNIL7ZPBWYI6L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H424YXGW7OKXS2NCAP35OP6Y4P4AW6VG/
- https://gcc.gnu.org/pipermail/gcc-patches/2021-September/579987
