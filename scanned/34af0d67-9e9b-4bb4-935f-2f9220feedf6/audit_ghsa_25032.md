# [C] qcubed SQL injection vulnerability in profile.php via the strQuery parameter

## Summary
Severity: Critical
Advisory: GHSA-8fj6-pc5r-347q
CVE: CVE-2020-24913
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8fj6-pc5r-347q
Type: github-advisory

## Affected
- Packagist: `qcubed/qcubed` — affected >=0 <3.2

## Details
A SQL injection vulnerability in qcubed (all versions including 3.1.1) in profile.php via the strQuery parameter allows an unauthenticated attacker to access the database by injecting SQL code via a crafted POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24913
- https://github.com/qcubed/qcubed/pull/1320/files
- https://github.com/qcubed/qcubed
- https://tech.feedyourhead.at/content/QCubed-SQL-Injection-CVE-2020-24913
- https://www.ait.ac.at/themen/cyber-security/pentesting/security-advisories/ait-sa-20210215-02
- http://qcubed.com
- http://seclists.org/fulldisclosure/2021/Mar/29
- http://seclists.org/fulldisclosure/2021/Mar/30
