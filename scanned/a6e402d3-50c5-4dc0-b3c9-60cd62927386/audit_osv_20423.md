# [M] CVE-2021-33515

## Summary
Severity: Medium
Advisory: CVE-2021-33515
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/CVE-2021-33515
Type: osv

## Details
The submission service in Dovecot before 2.3.15 allows STARTTLS command injection in lib-smtp. Sensitive information can be redirected to an attacker-controlled address.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JB2VTJ3G2ILYWH5Y2FTY2PUHT2MD6VMI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TK424DWFO2TKJYXZ2H3XL633TYJL4GQN/
- https://dovecot.org/security
- https://lists.debian.org/debian-lts-announce/2022/09/msg00032.html
- https://security.gentoo.org/glsa/202107-41
- https://www.openwall.com/lists/oss-security/2021/06/28/2
