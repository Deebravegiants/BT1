# [C] CVE-2018-12356

## Summary
Severity: Critical
Advisory: CVE-2018-12356
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12356
Type: osv

## Details
An issue was discovered in password-store.sh in pass in Simple Password Store 1.7.x before 1.7.2. The signature verification routine parses the output of GnuPG with an incomplete regular expression, which allows remote attackers to spoof file signatures on configuration files and extension scripts. Modifying the configuration file allows the attacker to inject additional encryption keys under their control, thereby disclosing passwords to the attacker. Modifying the extension scripts allows the attacker arbitrary code execution.

## References
- https://github.com/RUB-NDS/Johnny-You-Are-Fired/blob/master/paper/johnny-fired.pdf
- http://openwall.com/lists/oss-security/2018/06/14/3
- http://packetstormsecurity.com/files/152703/Johnny-You-Are-Fired.html
- http://www.openwall.com/lists/oss-security/2019/04/30/4
- http://seclists.org/fulldisclosure/2019/Apr/38
- https://lists.zx2c4.com/pipermail/password-store/2018-June/003308.html
- https://git.zx2c4.com/password-store/commit/?id=8683403b77f59c56fcb1f05c61ab33b9fd61a30d
- https://github.com/RUB-NDS/Johnny-You-Are-Fired
