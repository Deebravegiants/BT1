# [C] CVE-2017-5400

## Summary
Severity: Critical
Advisory: CVE-2017-5400
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5400
Type: osv

## Details
JIT-spray targeting asm.js combined with a heap spray allows for a bypass of ASLR and DEP protections leading to potential memory corruption attacks. This vulnerability affects Firefox < 52, Firefox ESR < 45.8, Thunderbird < 52, and Thunderbird < 45.8.

## References
- http://www.securitytracker.com/id/1037966
- https://security.gentoo.org/glsa/201705-06
- https://security.gentoo.org/glsa/201705-07
- https://www.mozilla.org/security/advisories/mfsa2017-05/
- https://www.mozilla.org/security/advisories/mfsa2017-06/
- http://rhn.redhat.com/errata/RHSA-2017-0461.html
- http://www.securityfocus.com/bid/96654
- https://www.debian.org/security/2017/dsa-3805
- https://www.debian.org/security/2017/dsa-3832
- https://www.mozilla.org/security/advisories/mfsa2017-07/
- https://www.mozilla.org/security/advisories/mfsa2017-09/
- http://rhn.redhat.com/errata/RHSA-2017-0459.html
- http://rhn.redhat.com/errata/RHSA-2017-0498.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1334933
