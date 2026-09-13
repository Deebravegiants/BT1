# [H] CVE-2017-5378

## Summary
Severity: High
Advisory: CVE-2017-5378
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5378
Type: osv

## Details
Hashed codes of JavaScript objects are shared between pages. This allows for pointer leaks because an object's address can be discovered through hash codes, and also allows for data leakage of an object's content using these hash codes. This vulnerability affects Thunderbird < 45.7, Firefox ESR < 45.7, and Firefox < 51.

## References
- https://security.gentoo.org/glsa/201702-13
- https://www.debian.org/security/2017/dsa-3832
- https://www.mozilla.org/security/advisories/mfsa2017-02/
- http://rhn.redhat.com/errata/RHSA-2017-0190.html
- http://www.securitytracker.com/id/1037693
- https://security.gentoo.org/glsa/201702-22
- https://www.debian.org/security/2017/dsa-3771
- https://www.mozilla.org/security/advisories/mfsa2017-01/
- https://www.mozilla.org/security/advisories/mfsa2017-03/
- http://rhn.redhat.com/errata/RHSA-2017-0238.html
- http://www.securityfocus.com/bid/95769
- https://bugzilla.mozilla.org/show_bug.cgi?id=1312001
- https://bugzilla.mozilla.org/show_bug.cgi?id=1330769
