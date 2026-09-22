# [M] simplejson before 2.6.1 vulnerable to array index error

## Summary
Severity: Medium
Advisory: GHSA-9772-cwx9-r4cj
CVE: CVE-2014-4616
CWE: CWE-129
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9772-cwx9-r4cj
Type: github-advisory

## Affected
- PyPI: `simplejson` — affected >=0 <2.6.1

## Details
Array index error in the scanstring function in the _json module in Python 2.7 through 3.5 and simplejson before 2.6.1 allows context-dependent attackers to read arbitrary process memory via a negative index value in the idx argument to the raw_decode function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4616
- https://hackerone.com/reports/12297
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=752395
- https://bugzilla.redhat.com/show_bug.cgi?id=1112285
- https://github.com/simplejson/simplejson
- https://security.gentoo.org/glsa/201503-10
- http://bugs.python.org/issue21529
- http://lists.opensuse.org/opensuse-updates/2014-07/msg00015.html
- http://openwall.com/lists/oss-security/2014/06/24/7
- http://rhn.redhat.com/errata/RHSA-2015-1064.html
- http://www.securityfocus.com/bid/68119
