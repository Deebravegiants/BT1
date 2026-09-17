# [C] CVE-2017-7828

## Summary
Severity: Critical
Advisory: CVE-2017-7828
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7828
Type: osv

## Details
A use-after-free vulnerability can occur when flushing and resizing layout because the "PressShell" object has been freed while still in use. This results in a potentially exploitable crash during these operations. This vulnerability affects Firefox < 57, Firefox ESR < 52.5, and Thunderbird < 52.5.

## References
- https://access.redhat.com/errata/RHSA-2017:3247
- https://access.redhat.com/errata/RHSA-2017:3372
- https://lists.debian.org/debian-lts-announce/2017/11/msg00018.html
- https://www.mozilla.org/security/advisories/mfsa2017-24/
- https://www.mozilla.org/security/advisories/mfsa2017-25/
- http://www.securityfocus.com/bid/101832
- https://lists.debian.org/debian-lts-announce/2017/12/msg00001.html
- https://www.debian.org/security/2017/dsa-4035
- https://www.debian.org/security/2017/dsa-4061
- https://www.debian.org/security/2017/dsa-4075
- https://www.mozilla.org/security/advisories/mfsa2017-26/
- http://www.securitytracker.com/id/1039803
- https://bugzilla.mozilla.org/show_bug.cgi?id=1406750
- https://bugzilla.mozilla.org/show_bug.cgi?id=1412252
