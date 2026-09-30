# [H] CVE-2023-36664

## Summary
Severity: High
Advisory: CVE-2023-36664
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-25
Source: https://osv.dev/vulnerability/CVE-2023-36664
Type: osv

## Details
Artifex Ghostscript through 10.01.2 mishandles permission validation for pipe devices (with the %pipe% prefix or the | pipe character prefix).

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=0974e4f2ac0005d3731e0b5c13ebc7e965540f4d
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=505eab7782b429017eb434b2b95120855f2b0e3c
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2ICXN5VPF3WJCYKMPSYER5KHTPJXSTJZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5EWMEK2UPCUU3ZLL7VASE5CEHDQY4VKV/
- https://security.gentoo.org/glsa/202309-03
- https://www.debian.org/security/2023/dsa-5446
- https://bugs.ghostscript.com/show_bug.cgi?id=706761
