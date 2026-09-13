# [M] MoinMoin Improper Access Control  

## Summary
Severity: Medium
Advisory: GHSA-jj2f-57jg-5rm6
CVE: CVE-2008-1099
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-jj2f-57jg-5rm6
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=0

## Details
`_macro_Getval` in `wikimacro.py` in MoinMoin 1.5.8 and earlier does not properly enforce ACLs, which allows remote attackers to read protected pages. The issue has been fixed on [4a7de0173734](http://hg.moinmo.in/moin/1.5/rev/4a7de0173734).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1099
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41038
- https://usn.ubuntu.com/716-1
- https://www.redhat.com/archives/fedora-package-announce/2008-April/msg00510.html
- https://www.redhat.com/archives/fedora-package-announce/2008-April/msg00538.html
- http://hg.moinmo.in/moin/1.5/rev/4a7de0173734
- http://moinmo.in/SecurityFixes
- http://secunia.com/advisories/29262
- http://secunia.com/advisories/29444
- http://secunia.com/advisories/30031
- http://secunia.com/advisories/33755
- http://www.debian.org/security/2008/dsa-1514
- http://www.gentoo.org/security/en/glsa/glsa-200803-27.xml
- http://www.securityfocus.com/bid/28177
