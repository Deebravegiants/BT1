# [H] CVE-2021-3156

## Summary
Severity: High
Advisory: CVE-2021-3156
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2021-3156
Type: osv

## Details
Sudo before 1.9.5p2 contains an off-by-one error that can result in a heap-based buffer overflow, which allows privilege escalation to root via "sudoedit -s" and a command-line argument that ends with a single backslash character.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-3156
- http://seclists.org/fulldisclosure/2021/Feb/42
- http://www.openwall.com/lists/oss-security/2021/01/27/1
- http://www.openwall.com/lists/oss-security/2021/01/27/2
- https://kc.mcafee.com/corporate/index?page=content&id=SB10348
- https://lists.debian.org/debian-lts-announce/2021/01/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CALA5FTXIQBRRYUA2ZQNJXB6OQMAXEII/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LHXK6ICO5AYLGFK2TAX5MZKUXTUKWOJY/
- https://security.gentoo.org/glsa/202101-33
- https://security.netapp.com/advisory/ntap-20210128-0001/
- https://security.netapp.com/advisory/ntap-20210128-0002/
- https://support.apple.com/kb/HT212177
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-sudo-privesc-jan2021-qnYQfcM
- https://www.beyondtrust.com/blog/entry/security-advisory-privilege-management-for-unix-linux-pmul-basic-and-privilege-management-for-mac-pmm-affected-by-sudo-vulnerability
- https://www.debian.org/security/2021/dsa-4839
- https://www.kb.cert.org/vuls/id/794544
- https://www.sudo.ws/stable.html#1.9.5p2
- https://www.synology.com/security/advisory/Synology_SA_21_02
- http://www.openwall.com/lists/oss-security/2021/09/14/2
- https://www.oracle.com//security-alerts/cpujul2021.html
