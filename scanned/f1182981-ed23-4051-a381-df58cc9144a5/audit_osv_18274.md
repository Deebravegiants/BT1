# [H] CVE-2020-25719

## Summary
Severity: High
Advisory: CVE-2020-25719
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2020-25719
Type: osv

## Details
A flaw was found in the way Samba, as an Active Directory Domain Controller, implemented Kerberos name-based authentication. The Samba AD DC, could become confused about the user a ticket represents if it did not strictly require a Kerberos PAC and always use the SIDs found within. The result could include total domain compromise.

## References
- https://security.gentoo.org/glsa/202309-06
- https://www.samba.org/samba/security/CVE-2020-25719.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2019732
