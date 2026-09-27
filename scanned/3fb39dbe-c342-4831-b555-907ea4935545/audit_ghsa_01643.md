# [C] SQL injection in Centreon

## Summary
Severity: Critical
Advisory: GHSA-wgjx-hm34-qgf7
CVE: CVE-2019-16194
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-11
Source: https://github.com/advisories/GHSA-wgjx-hm34-qgf7
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <18.10.8
- Packagist: `centreon/centreon` — affected >=19.0.0 <19.04.5

## Details
SQL injection vulnerabilities in Centreon through 19.04 allow attacks via the svc_id parameter in include/monitoring/status/Services/xml/makeXMLForOneService.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16194
- https://github.com/centreon/centreon/pull/7862
- https://github.com/centreon/centreon/releases
