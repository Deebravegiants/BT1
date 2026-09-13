# [M] CVE-2018-16857

## Summary
Severity: Medium
Advisory: CVE-2018-16857
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-16857
Type: osv

## Details
Samba from version 4.9.0 and before version 4.9.3 that have AD DC configurations watching for bad passwords (to restrict brute forcing of passwords) in a window of more than 3 minutes may not watch for bad passwords at all. The primary risk from this issue is with regards to domains that have been upgraded from Samba 4.8 and earlier. In these cases the manual testing done to confirm an organisation's password policies apply as expected may not have been re-done after the upgrade.

## References
- http://www.securityfocus.com/bid/106024
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20181127-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16857
- https://www.samba.org/samba/security/CVE-2018-16857.html
