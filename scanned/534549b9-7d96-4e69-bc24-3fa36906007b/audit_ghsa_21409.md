# [C] Centreon vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-j5wx-jvw3-j363
CVE: CVE-2022-3827
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-02
Source: https://github.com/advisories/GHSA-j5wx-jvw3-j363
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0 <22.10.0-beta1

## Details
A SQL injection vulnerability in Centreon affects unknown code of the file formContactGroup.php of the component Contact Groups Form. The manipulation of the argument cg_id leads to sql injection. The attack can be initiated remotely. Version 22.10.0-beta1 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3827
- https://github.com/centreon/centreon/pull/11869
- https://github.com/centreon/centreon/commit/293b10628f7d9f83c6c82c78cf637cbe9b907369
- https://github.com/centreon/centreon
- https://vuldb.com/?id.212794
