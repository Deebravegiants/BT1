# [M] Zope DocumentTemplate package allows unauthenticated write

## Summary
Severity: Medium
Advisory: GHSA-j5cc-3h6r-jqh4
CVE: CVE-2000-0483
CWE: CWE-287
Ecosystem: PyPI
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-j5cc-3h6r-jqh4
Type: github-advisory

## Affected
- PyPI: `zope` — affected >=0

## Details
The DocumentTemplate package in Zope 2.2 and earlier allows a remote attacker to modify DTMLDocuments or DTMLMethods without authorization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2000-0483
- https://exchange.xforce.ibmcloud.com/vulnerabilities/4716
- https://web.archive.org/web/20000819120649/http://archives.neohapsis.com/archives/bugtraq/2000-06/0144.html
- https://web.archive.org/web/20000819123924/http://archives.neohapsis.com/archives/bugtraq/2000-07/0412.html
- https://web.archive.org/web/20010702023709/http://www.securityfocus.com/bid/1354
- http://www.redhat.com/support/errata/RHSA-2000-038.html
- http://www.zope.org/Products/Zope/Hotfix_06_16_2000/security_alert
