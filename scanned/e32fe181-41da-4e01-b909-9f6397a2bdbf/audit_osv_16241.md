# [H] CVE-2019-3813

## Summary
Severity: High
Advisory: CVE-2019-3813
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-3813
Type: osv

## Details
Spice, versions 0.5.2 through 0.14.1, are vulnerable to an out-of-bounds read due to an off-by-one error in memslot_get_virt. This may lead to a denial of service, or, in the worst case, code-execution by unauthenticated attackers.

## References
- http://www.securityfocus.com/bid/106801
- https://access.redhat.com/errata/RHSA-2019:0231
- https://access.redhat.com/errata/RHSA-2019:0232
- https://access.redhat.com/errata/RHSA-2019:0457
- https://lists.debian.org/debian-lts-announce/2019/01/msg00026.html
- https://security.gentoo.org/glsa/202007-30
- https://usn.ubuntu.com/3870-1/
- https://www.debian.org/security/2019/dsa-4375
- https://bugzilla.redhat.com/show_bug.cgi?id=1665371
