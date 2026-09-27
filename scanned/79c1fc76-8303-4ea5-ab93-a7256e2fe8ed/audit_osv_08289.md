# [M] CVE-2016-2124

## Summary
Severity: Medium
Advisory: CVE-2016-2124
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2016-2124
Type: osv

## Details
A flaw was found in the way samba implemented SMB1 authentication. An attacker could use this flaw to retrieve the plaintext password sent over the wire even if Kerberos authentication was required.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00013.html
- https://security.gentoo.org/glsa/202309-06
- https://www.samba.org/samba/security/CVE-2016-2124.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2019660
