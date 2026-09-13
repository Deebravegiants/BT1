# [C] CVE-2017-2640

## Summary
Severity: Critical
Advisory: CVE-2017-2640
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2640
Type: osv

## Details
An out-of-bounds write flaw was found in the way Pidgin before 2.12.0 processed XML content. A malicious remote server could potentially use this flaw to crash Pidgin or execute arbitrary code in the context of the pidgin process.

## References
- https://security.gentoo.org/glsa/201706-10
- https://www.debian.org/security/2017/dsa-3806
- http://www.securityfocus.com/bid/96775
- https://access.redhat.com/errata/RHSA-2017:1854
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2640
