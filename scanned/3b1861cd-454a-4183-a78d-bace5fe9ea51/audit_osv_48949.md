# [C] CVE-2018-18500

## Summary
Severity: Critical
Advisory: CVE-2018-18500
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/CVE-2018-18500
Type: osv

## Details
A use-after-free vulnerability can occur while parsing an HTML5 stream in concert with custom HTML elements. This results in the stream parser object being freed while still in use, leading to a potentially exploitable crash. This vulnerability affects Thunderbird < 60.5, Firefox ESR < 60.5, and Firefox < 65.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00021.html
- https://www.debian.org/security/2019/dsa-4392
- https://access.redhat.com/errata/RHSA-2019:0219
- https://security.gentoo.org/glsa/201904-07
- https://usn.ubuntu.com/3874-1/
- https://www.mozilla.org/security/advisories/mfsa2019-03/
- https://lists.debian.org/debian-lts-announce/2019/02/msg00024.html
- https://www.mozilla.org/security/advisories/mfsa2019-01/
- https://usn.ubuntu.com/3897-1/
- http://www.securityfocus.com/bid/106781
- https://access.redhat.com/errata/RHSA-2019:0218
- https://access.redhat.com/errata/RHSA-2019:0270
- https://security.gentoo.org/glsa/201903-04
- https://access.redhat.com/errata/RHSA-2019:0269
- https://lists.debian.org/debian-lts-announce/2019/01/msg00025.html
- https://www.debian.org/security/2019/dsa-4376
- https://www.mozilla.org/security/advisories/mfsa2019-02/
