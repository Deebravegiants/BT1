# [C] CVE-2018-18498

## Summary
Severity: Critical
Advisory: CVE-2018-18498
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2018-18498
Type: osv

## Details
A potential vulnerability leading to an integer overflow can occur during buffer size calculations for images when a raw value is used instead of the checked value. This leads to a possible out-of-bounds write. This vulnerability affects Thunderbird < 60.4, Firefox ESR < 60.4, and Firefox < 64.

## References
- https://access.redhat.com/errata/RHSA-2018:3833
- https://www.debian.org/security/2018/dsa-4354
- https://www.mozilla.org/security/advisories/mfsa2018-29/
- http://www.securityfocus.com/bid/106168
- https://access.redhat.com/errata/RHSA-2018:3831
- https://lists.debian.org/debian-lts-announce/2018/12/msg00002.html
- https://www.mozilla.org/security/advisories/mfsa2018-30/
- https://www.mozilla.org/security/advisories/mfsa2018-31/
- https://usn.ubuntu.com/3844-1/
- https://access.redhat.com/errata/RHSA-2019:0159
- https://access.redhat.com/errata/RHSA-2019:0160
- https://security.gentoo.org/glsa/201903-04
- https://usn.ubuntu.com/3868-1/
- https://www.debian.org/security/2019/dsa-4362
- https://bugzilla.mozilla.org/show_bug.cgi?id=1500011
