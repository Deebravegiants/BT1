# [C] CVE-2021-33833

## Summary
Severity: Critical
Advisory: CVE-2021-33833
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-09
Source: https://osv.dev/vulnerability/CVE-2021-33833
Type: osv

## Details
ConnMan (aka Connection Manager) 1.30 through 1.39 has a stack-based buffer overflow in uncompress in dnsproxy.c via NAME, RDATA, or RDLENGTH (for A or AAAA).

## References
- http://www.openwall.com/lists/oss-security/2021/06/09/1
- https://lists.debian.org/debian-lts-announce/2022/02/msg00009.html
- https://lore.kernel.org/connman/
- https://security.gentoo.org/glsa/202107-29
- http://www.openwall.com/lists/oss-security/2022/01/25/1
