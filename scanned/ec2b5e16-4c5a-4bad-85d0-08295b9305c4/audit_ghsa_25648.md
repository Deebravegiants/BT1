# [H] Zope does not properly perform security registration for legacy names

## Summary
Severity: High
Advisory: GHSA-h2xh-jvpf-xq42
CVE: CVE-2000-1211
CWE: CWE-287
Ecosystem: PyPI
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-h2xh-jvpf-xq42
Type: github-advisory

## Affected
- PyPI: `zope` — affected >=2.2.0

## Details
Zope 2.2.0 through 2.2.4 does not properly perform security registration for legacy names of object constructors such as DTML method objects, which could allow attackers to perform unauthorized activities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2000-1211
- https://web.archive.org/web/20010910131909/http://www.linux-mandrake.com/en/security/2000/MDKSA-2000-083.php3
- https://web.archive.org/web/20021227061438/http://www.iss.net/security_center/static/5824.php
- http://www.redhat.com/support/errata/RHSA-2000-125.html
- http://www.zope.org/Products/Zope/Hotfix_2000-12-08/security_alert
