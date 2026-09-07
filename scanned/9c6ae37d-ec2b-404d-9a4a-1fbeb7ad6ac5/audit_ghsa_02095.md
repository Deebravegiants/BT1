# [M] lxml vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-pgww-xf46-h92r
CVE: CVE-2020-27783
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-01-07
Source: https://github.com/advisories/GHSA-pgww-xf46-h92r
Type: github-advisory

## Affected
- PyPI: `lxml` — affected >=0 <4.6.2

## Details
A XSS vulnerability was discovered in python-lxml's clean module. The module's parser didn't properly imitate browsers, which caused different behaviors between the sanitizer and the user's page. A remote attacker could exploit this flaw to run arbitrary HTML/JS code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27783
- https://github.com/lxml/lxml/commit/a105ab8dc262ec6735977c25c13f0bdfcdec72a7
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.debian.org/security/2020/dsa-4810
- https://snyk.io/vuln/SNYK-PYTHON-LXML-1047473
- https://security.netapp.com/advisory/ntap-20210521-0003
- https://pypi.org/project/lxml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TMHVKRUT22LVWNL3TB7HPSDHJT74Q3JK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JKG67GPGTV23KADT4D4GK4RMHSO4CIQL
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TMHVKRUT22LVWNL3TB7HPSDHJT74Q3JK
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JKG67GPGTV23KADT4D4GK4RMHSO4CIQL
- https://lists.debian.org/debian-lts-announce/2020/12/msg00028.html
- https://github.com/pypa/advisory-database/tree/main/vulns/lxml/PYSEC-2020-62.yaml
- https://github.com/lxml/lxml
- https://github.com/advisories/GHSA-pgww-xf46-h92r
- https://bugzilla.redhat.com/show_bug.cgi?id=1901633
- https://advisory.checkmarx.net/advisory/CX-2020-4286
