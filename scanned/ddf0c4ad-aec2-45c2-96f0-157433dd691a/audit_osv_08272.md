# [M] CVE-2016-2100

## Summary
Severity: Medium
Advisory: CVE-2016-2100
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2016-05-20
Source: https://osv.dev/vulnerability/CVE-2016-2100
Type: osv

## Details
Foreman before 1.10.3 and 1.11.0 before 1.11.0-RC2 allow remote authenticated users to read, modify, or delete private bookmarks by leveraging the (1) edit_bookmarks or (2) destroy_bookmarks permission.

## References
- http://projects.theforeman.org/issues/13828
- http://www.openwall.com/lists/oss-security/2016/03/31/2
- http://theforeman.org/security.html#2016-2100
- https://access.redhat.com/errata/RHBA-2016:1500
