# [M] CVE-2018-10845

## Summary
Severity: Medium
Advisory: CVE-2018-10845
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/CVE-2018-10845
Type: osv

## Details
It was found that the GnuTLS implementation of HMAC-SHA-384 was vulnerable to a Lucky thirteen style attack. Remote attackers could use this flaw to conduct distinguishing attacks and plain text recovery attacks via statistical analysis of timing data using crafted packets.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ILMOWPKMTZAIMK5F32TUMO34XCABUCFJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WDYY3R4F5CUTFAMXH2C5NKYFVDEJLTT7/
- http://www.securityfocus.com/bid/105138
- https://access.redhat.com/errata/RHSA-2018:3050
- https://access.redhat.com/errata/RHSA-2018:3505
- https://eprint.iacr.org/2018/747
- https://lists.debian.org/debian-lts-announce/2018/10/msg00022.html
- https://usn.ubuntu.com/3999-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10845
- https://gitlab.com/gnutls/gnutls/merge_requests/657
