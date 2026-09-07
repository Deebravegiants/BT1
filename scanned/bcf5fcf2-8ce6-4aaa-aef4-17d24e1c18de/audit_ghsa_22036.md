# [M] MoinMoin Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-53wj-6m7w-j6mj
CVE: CVE-2008-0780
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-53wj-6m7w-j6mj
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=1.5
- PyPI: `moin` — affected >=1.6 <1.6.1

## Details
Cross-site scripting (XSS) vulnerability in MoinMoin 1.5.x through 1.5.8 and 1.6.x before 1.6.1 allows remote attackers to inject arbitrary web script or HTML via the login action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-0780
- https://bugzilla.redhat.com/show_bug.cgi?id=432747
- https://usn.ubuntu.com/716-1
- https://www.redhat.com/archives/fedora-package-announce/2008-February/msg00726.html
- https://www.redhat.com/archives/fedora-package-announce/2008-February/msg00752.html
- http://hg.moinmo.in/moin/1.5/rev/2f952fa361c7
- http://hg.moinmo.in/moin/1.6/rev/9f4bdc7ef80d
- http://secunia.com/advisories/28987
- http://secunia.com/advisories/29010
- http://secunia.com/advisories/29262
- http://secunia.com/advisories/29444
- http://secunia.com/advisories/33755
- http://www.debian.org/security/2008/dsa-1514
- http://www.gentoo.org/security/en/glsa/glsa-200803-27.xml
- http://www.securityfocus.com/bid/27904
- http://www.vupen.com/english/advisories/2008/0569/references
