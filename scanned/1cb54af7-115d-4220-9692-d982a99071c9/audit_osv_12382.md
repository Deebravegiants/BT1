# [C] CVE-2018-1160

## Summary
Severity: Critical
Advisory: CVE-2018-1160
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1160
Type: osv

## Details
Netatalk before 3.1.12 is vulnerable to an out of bounds write in dsi_opensess.c. This is due to lack of bounds checking on attacker controlled data. A remote unauthenticated attacker can leverage this vulnerability to achieve arbitrary code execution.

## References
- http://netatalk.sourceforge.net/3.1/ReleaseNotes3.1.12.html
- http://www.securityfocus.com/bid/106301
- https://attachments.samba.org/attachment.cgi?id=14735
- https://github.com/tenable/poc/tree/master/netatalk/cve_2018_1160/
- https://www.debian.org/security/2018/dsa-4356
- https://www.synology.com/security/advisory/Synology_SA_18_62
- http://packetstormsecurity.com/files/152440/QNAP-Netatalk-Authentication-Bypass.html
- https://www.exploit-db.com/exploits/46034/
- https://www.exploit-db.com/exploits/46048/
- https://www.exploit-db.com/exploits/46675/
- https://www.tenable.com/security/research/tra-2018-48
