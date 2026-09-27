# [H] CVE-2018-16860

## Summary
Severity: High
Advisory: CVE-2018-16860
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2018-16860
Type: osv

## Details
A flaw was found in samba's Heimdal KDC implementation, versions 4.8.x up to, excluding 4.8.12, 4.9.x up to, excluding 4.9.8 and 4.10.x up to, excluding 4.10.3, when used in AD DC mode. A man in the middle attacker could use this flaw to intercept the request to the KDC and replace the user name (principal) in the request with any desired user name (principal) that exists in the KDC effectively obtaining a ticket for that principal.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00026.html
- http://seclists.org/fulldisclosure/2019/Aug/11
- http://seclists.org/fulldisclosure/2019/Aug/13
- http://seclists.org/fulldisclosure/2019/Aug/14
- http://seclists.org/fulldisclosure/2019/Aug/15
- https://seclists.org/bugtraq/2019/Aug/21
- https://seclists.org/bugtraq/2019/Aug/22
- https://seclists.org/bugtraq/2019/Aug/23
- https://seclists.org/bugtraq/2019/Aug/25
- https://support.apple.com/HT210346
- https://support.apple.com/HT210348
- https://support.apple.com/HT210351
- https://support.apple.com/HT210353
- https://security.gentoo.org/glsa/202003-52
- https://www.samba.org/samba/security/CVE-2018-16860.html
- https://www.synology.com/security/advisory/Synology_SA_19_23
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16860
