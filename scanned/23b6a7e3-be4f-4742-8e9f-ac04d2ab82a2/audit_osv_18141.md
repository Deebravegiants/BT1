# [M] CVE-2020-24386

## Summary
Severity: Medium
Advisory: CVE-2020-24386
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-01-04
Source: https://osv.dev/vulnerability/CVE-2020-24386
Type: osv

## Details
An issue was discovered in Dovecot before 2.3.13. By using IMAP IDLE, an authenticated attacker can trigger unhibernation via attacker-controlled parameters, leading to access to other users' email messages (and path disclosure).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GXDKFLOCUP7I4ELGQ2F4P5TGC6NXMYV7/
- http://packetstormsecurity.com/files/160842/Dovecot-2.3.11.3-Access-Bypass.html
- http://seclists.org/fulldisclosure/2021/Jan/18
- http://www.openwall.com/lists/oss-security/2021/01/04/4
- https://doc.dovecot.org/configuration_manual/hibernation/
- https://dovecot.org/pipermail/dovecot-news/2021-January/000450.html
- https://dovecot.org/security
- https://security.gentoo.org/glsa/202101-01
- https://www.debian.org/security/2021/dsa-4825
