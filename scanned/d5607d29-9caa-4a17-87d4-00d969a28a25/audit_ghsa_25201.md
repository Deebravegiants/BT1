# [M] MoinMoin has multiple vulnerabilities related to superuser list, xmlrpc and OpenID configuration

## Summary
Severity: Medium
Advisory: GHSA-574f-mh6m-c6qm
CVE: CVE-2010-0668
Ecosystem: PyPI
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-574f-mh6m-c6qm
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=1.5 <1.8.7
- PyPI: `moin` — affected >=1.9 <1.9.2

## Details
Unspecified vulnerability in MoinMoin 1.5.x through 1.7.x, 1.8.x before 1.8.7, and 1.9.x before 1.9.2 has unknown impact and attack vectors, related to configurations that have a non-empty superuser list, the xmlrpc action enabled, the SyncPages action enabled, or OpenID configured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-0668
- https://bugzilla.redhat.com/show_bug.cgi?id=565604
- https://exchange.xforce.ibmcloud.com/vulnerabilities/56002
- https://github.com/moinwiki/moin
- https://github.com/pypa/advisory-database/tree/main/vulns/moin/PYSEC-2010-15.yaml
- https://web.archive.org/web/20111225112846/http://secunia.com/advisories/38903
- https://web.archive.org/web/20140725192956/http://secunia.com/advisories/38709
- https://web.archive.org/web/20140806190238/http://secunia.com/advisories/38444
- https://web.archive.org/web/20200228174758/http://www.securityfocus.com/bid/38023
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=569975
- http://hg.moinmo.in/moin/1.8/raw-file/1.8.7/docs/CHANGES
- http://lists.fedoraproject.org/pipermail/package-announce/2010-February/035374.html
- http://lists.fedoraproject.org/pipermail/package-announce/2010-February/035438.html
- http://marc.info/?l=oss-security&m=126625972814888&w=2
- http://marc.info/?l=oss-security&m=126676896601156&w=2
- http://moinmo.in/MoinMoinRelease1.8
- http://moinmo.in/SecurityFixes
- http://www.debian.org/security/2010/dsa-2014
- http://www.openwall.com/lists/oss-security/2010/02/15/2
