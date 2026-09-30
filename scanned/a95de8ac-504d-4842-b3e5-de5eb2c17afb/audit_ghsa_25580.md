# [H] Zope does not properly verify the access for objects with proxy roles

## Summary
Severity: High
Advisory: GHSA-c3rp-4cjh-cp38
CVE: CVE-2002-0170
CWE: CWE-284
Ecosystem: PyPI
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-c3rp-4cjh-cp38
Type: github-advisory

## Affected
- PyPI: `zope` — affected >=2.2.0 <2.4.4
- PyPI: `zope` — affected >=2.5.0 <2.5.1

## Details
Zope 2.2.0 through 2.5.1 does not properly verify the access for objects with proxy roles, which could allow some users to access documents in violation of the intended configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2002-0170
- https://github.com/zopefoundation/Zope
- https://launchpad.net/zope2/+milestone/2.4.4
- https://launchpad.net/zope2/+milestone/2.5.1
- https://web.archive.org/web/20021120034302/http://online.securityfocus.com/bid/4229
- https://web.archive.org/web/20070914020022/http://xforce.iss.net/xforce/xfdb/8334
- http://marc.info/?l=bugtraq&m=101503023511996&w=2
- http://www.redhat.com/support/errata/RHSA-2002-060.html
