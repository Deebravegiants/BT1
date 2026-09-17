# [H] CVE-2018-1139

## Summary
Severity: High
Advisory: CVE-2018-1139
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/CVE-2018-1139
Type: osv

## Details
A flaw was found in the way samba before 4.7.9 and 4.8.4 allowed the use of weak NTLMv1 authentication even when NTLMv1 was explicitly disabled. A man-in-the-middle attacker could use this flaw to read the credential and other details passed between the samba server and client.

## References
- http://www.securityfocus.com/bid/105084
- https://access.redhat.com/errata/RHSA-2018:2612
- https://access.redhat.com/errata/RHSA-2018:2613
- https://access.redhat.com/errata/RHSA-2018:3056
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20180814-0001/
- https://usn.ubuntu.com/3738-1/
- https://www.samba.org/samba/security/CVE-2018-1139.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1139
