# [H] CVE-2022-30333

## Summary
Severity: High
Advisory: CVE-2022-30333
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-05-09
Source: https://osv.dev/vulnerability/CVE-2022-30333
Type: osv

## Details
RARLAB UnRAR before 6.12 on Linux and UNIX allows directory traversal to write to files during an extract (aka unpack) operation, as demonstrated by creating a ~/.ssh/authorized_keys file. NOTE: WinRAR and Android RAR are unaffected.

## References
- https://www.rarlab.com/rar_add.htm
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-30333
- https://lists.debian.org/debian-lts-announce/2023/08/msg00022.html
- https://security.gentoo.org/glsa/202309-04
- https://www.rarlab.com/rar/rarlinux-x32-612.tar.gz
- http://packetstormsecurity.com/files/167989/Zimbra-UnRAR-Path-Traversal.html
- https://blog.sonarsource.com/zimbra-pre-auth-rce-via-unrar-0day/
