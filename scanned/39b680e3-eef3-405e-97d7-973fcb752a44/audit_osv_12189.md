# [M] CVE-2018-10846

## Summary
Severity: Medium
Advisory: CVE-2018-10846
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/CVE-2018-10846
Type: osv

## Details
A cache-based side channel in GnuTLS implementation that leads to plain text recovery in cross-VM attack setting was found. An attacker could use a combination of "Just in Time" Prime+probe attack in combination with Lucky-13 attack to recover plain text using crafted packets.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ILMOWPKMTZAIMK5F32TUMO34XCABUCFJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WDYY3R4F5CUTFAMXH2C5NKYFVDEJLTT7/
- http://www.securityfocus.com/bid/105138
- https://access.redhat.com/errata/RHSA-2018:3050
- https://access.redhat.com/errata/RHSA-2018:3505
- https://eprint.iacr.org/2018/747
- https://lists.debian.org/debian-lts-announce/2018/10/msg00022.html
- https://usn.ubuntu.com/3999-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10846
- https://gitlab.com/gnutls/gnutls/merge_requests/657
