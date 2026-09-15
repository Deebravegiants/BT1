# [H] CVE-2017-7807

## Summary
Severity: High
Advisory: CVE-2017-7807
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7807
Type: osv

## Details
A mechanism that uses AppCache to hijack a URL in a domain using fallback by serving the files from a sub-path on the domain. This has been addressed by requiring fallback files be inside the manifest directory. This vulnerability affects Thunderbird < 52.3, Firefox ESR < 52.3, and Firefox < 55.

## References
- http://www.securityfocus.com/bid/100242
- http://www.securitytracker.com/id/1039124
- https://access.redhat.com/errata/RHSA-2017:2456
- https://access.redhat.com/errata/RHSA-2017:2534
- https://security.gentoo.org/glsa/201803-14
- https://www.debian.org/security/2017/dsa-3968
- https://www.mozilla.org/security/advisories/mfsa2017-18/
- https://www.mozilla.org/security/advisories/mfsa2017-20/
- https://www.debian.org/security/2017/dsa-3928
- https://www.mozilla.org/security/advisories/mfsa2017-19/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1376459
