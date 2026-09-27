# [H] MoinMoin Access Restrictions Bypassed due to improper ACL enforcement

## Summary
Severity: High
Advisory: GHSA-wc8w-gh5m-62fv
CVE: CVE-2008-6603
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wc8w-gh5m-62fv
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=0 <1.6.3
- PyPI: `moin` — affected >=1.7 <1.7.1

## Details
MoinMoin 1.6.2 and 1.7 does not properly enforce ACL checks when acl_hierarchic is set to True, which might allow remote attackers to bypass intended access restrictions, a different vulnerability than CVE-2008-1937.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-6603
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41911
- https://github.com/moinwiki/moin
- https://github.com/pypa/advisory-database/tree/main/vulns/moin/PYSEC-2009-13.yaml
- https://web.archive.org/web/20080511110948/http://hg.moinmo.in/moin/1.6/rev/543ae9bdbe26
- https://web.archive.org/web/20090730023652/http://moinmo.in/MoinMoinBugs/AclHierarchicPageAclSupercededByAclRightsAfter
- https://web.archive.org/web/20200301063229/http://www.securityfocus.com/bid/34655
- https://web.archive.org/web/20211207023130/http://hg.moinmo.in/moin/1.7/rev/88356b3f849a
- http://hg.moinmo.in/moin/1.6/rev/543ae9bdbe26
- http://hg.moinmo.in/moin/1.7/rev/88356b3f849a
- http://moinmo.in/MoinMoinBugs/AclHierarchicPageAclSupercededByAclRightsAfter
- http://moinmo.in/SecurityFixes
- http://osvdb.org/48875
- http://www.securityfocus.com/bid/34655
- http://www.vupen.com/english/advisories/2008/1307
