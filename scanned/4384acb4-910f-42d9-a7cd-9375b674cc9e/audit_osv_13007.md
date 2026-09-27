# [M] CVE-2018-16853

## Summary
Severity: Medium
Advisory: CVE-2018-16853
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-16853
Type: osv

## Details
Samba from version 4.7.0 has a vulnerability that allows a user in a Samba AD domain to crash the KDC when Samba is built in the non-default MIT Kerberos configuration. With this advisory the Samba Team clarify that the MIT Kerberos build of the Samba AD DC is considered experimental. Therefore the Samba Team will not issue security patches for this configuration. Additionally, Samba 4.7.12, 4.8.7 and 4.9.3 have been issued as security releases to prevent building of the AD DC with MIT Kerberos unless --with-experimental-mit-ad-dc is specified to the configure command.

## References
- http://www.securityfocus.com/bid/106026
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20181127-0001/
- https://www.samba.org/samba/security/CVE-2018-16853.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16853
