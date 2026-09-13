# [M] CVE-2021-20316

## Summary
Severity: Medium
Advisory: CVE-2021-20316
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-20316
Type: osv

## Details
A flaw was found in the way Samba handled file/directory metadata. This flaw allows an authenticated attacker with permissions to read or modify share metadata, to perform this operation outside of the share.

## References
- https://access.redhat.com/security/cve/CVE-2021-20316
- https://security-tracker.debian.org/tracker/CVE-2021-20316
- https://security.gentoo.org/glsa/202309-06
- https://www.samba.org/samba/security/CVE-2021-20316.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2009673
- https://bugzilla.samba.org/show_bug.cgi?id=14842
