# [H] CVE-2016-9904

## Summary
Severity: High
Advisory: CVE-2016-9904
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2016-9904
Type: osv

## Details
An attacker could use a JavaScript Map/Set timing attack to determine whether an atom is used by another compartment/zone in specific contexts. This could be used to leak information, such as usernames embedded in JavaScript code, across websites. This vulnerability affects Firefox < 50.1, Firefox ESR < 45.6, and Thunderbird < 45.6.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2946.html
- https://security.gentoo.org/glsa/201701-15
- https://www.debian.org/security/2017/dsa-3757
- https://www.mozilla.org/security/advisories/mfsa2016-95/
- https://www.mozilla.org/security/advisories/mfsa2016-96/
- http://www.securityfocus.com/bid/94885
- http://www.securitytracker.com/id/1037461
- https://www.mozilla.org/security/advisories/mfsa2016-94/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1317936
