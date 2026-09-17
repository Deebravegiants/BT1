# [H] CVE-2017-7803

## Summary
Severity: High
Advisory: CVE-2017-7803
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7803
Type: osv

## Details
When a page's content security policy (CSP) header contains a "sandbox" directive, other directives are ignored. This results in the incorrect enforcement of CSP. This vulnerability affects Thunderbird < 52.3, Firefox ESR < 52.3, and Firefox < 55.

## References
- https://www.mozilla.org/security/advisories/mfsa2017-19/
- https://access.redhat.com/errata/RHSA-2017:2456
- https://access.redhat.com/errata/RHSA-2017:2534
- https://www.debian.org/security/2017/dsa-3928
- https://www.mozilla.org/security/advisories/mfsa2017-20/
- http://www.securityfocus.com/bid/100234
- http://www.securitytracker.com/id/1039124
- https://security.gentoo.org/glsa/201803-14
- https://www.debian.org/security/2017/dsa-3968
- https://www.mozilla.org/security/advisories/mfsa2017-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1377426
