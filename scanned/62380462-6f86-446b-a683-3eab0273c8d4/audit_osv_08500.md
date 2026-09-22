# [H] CVE-2016-3959

## Summary
Severity: High
Advisory: CVE-2016-3959
Aliases: GO-2022-0166
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-3959
Type: osv

## Details
The Verify function in crypto/dsa/dsa.go in Go before 1.5.4 and 1.6.x before 1.6.1 does not properly check parameters passed to the big integer library, which might allow remote attackers to cause a denial of service (infinite loop) via a crafted public key to a program that uses HTTPS client certificates or SSH server libraries.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182526.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183106.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183137.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00077.html
- http://www.openwall.com/lists/oss-security/2016/04/05/1
- http://www.openwall.com/lists/oss-security/2016/04/05/2
- https://go-review.googlesource.com/#/c/21533/
- https://groups.google.com/forum/#%21topic/golang-announce/9eqIHqaWvck
- http://rhn.redhat.com/errata/RHSA-2016-1538.html
