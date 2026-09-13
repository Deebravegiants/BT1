# [H] Zope does not properly restrict access to the getRoles method

## Summary
Severity: High
Advisory: GHSA-9cmq-pj6p-hgwf
CVE: CVE-2000-0725
CWE: CWE-284
Ecosystem: PyPI
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-9cmq-pj6p-hgwf
Type: github-advisory

## Affected
- PyPI: `zope` — affected >=0 <2.2.1

## Details
Zope before 2.2.1 does not properly restrict access to the getRoles method, which allows users who can edit DTML to add or modify roles by modifying the roles list that is included in a request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2000-0725
- https://web.archive.org/web/20010219192346/http://archives.neohapsis.com/archives/bugtraq/2000-08/0198.html
- https://web.archive.org/web/20010219192441/http://archives.neohapsis.com/archives/bugtraq/2000-08/0259.html
- https://web.archive.org/web/20010228172804/http://www.securityfocus.com/bid/1577
- http://www.debian.org/security/2000/20000821
- http://www.redhat.com/support/errata/RHSA-2000-052.html
- http://www.zope.org/Products/Zope/Hotfix_08_09_2000/security_alert
