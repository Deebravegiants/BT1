# [H] MoinMoin vulnerable to privilege escalation

## Summary
Severity: High
Advisory: GHSA-rqxp-6926-hphr
CVE: CVE-2008-1937
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-rqxp-6926-hphr
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=0 <1.6.3

## Details
The user form processing (userform.py) in MoinMoin before 1.6.3, when using ACLs or a non-empty superusers list, does not properly manage users, which allows remote attackers to gain privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1937
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41909
- https://github.com/moinwiki/moin
- https://github.com/pypa/advisory-database/tree/main/vulns/moin/PYSEC-2008-12.yaml
- https://web.archive.org/web/20080628213526/http://secunia.com/advisories/29894
- https://web.archive.org/web/20080724211750/http://www.securityfocus.com/bid/28869
- https://web.archive.org/web/20081002145815/http://hg.moinmo.in/moin/1.6/rev/f405012e67af
- https://web.archive.org/web/20081007072837/http://secunia.com/advisories/30160
- http://moinmo.in/SecurityFixes
- http://security.gentoo.org/glsa/glsa-200805-09.xml
