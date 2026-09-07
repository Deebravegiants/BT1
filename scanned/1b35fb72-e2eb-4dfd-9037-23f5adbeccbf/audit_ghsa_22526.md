# [M] qcubed reflected cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xj4v-gp4q-h6qq
CVE: CVE-2020-24912
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xj4v-gp4q-h6qq
Type: github-advisory

## Affected
- Packagist: `qcubed/qcubed` — affected >=0 <3.2

## Details
A reflected cross-site scripting (XSS) vulnerability in qcubed (all versions including 3.1.1) in profile.php via the stQuery-parameter allows unauthenticated attackers to steal sessions of authenticated users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24912
- https://github.com/qcubed/qcubed/pull/1320/files
- https://github.com/qcubed/qcubed
- https://tech.feedyourhead.at/content/QCubed-Cross-Site-Scripting-CVE-2020-24912
- https://www.ait.ac.at/themen/cyber-security/pentesting/security-advisories/ait-sa-20210215-03
- http://qcubed.com
- http://seclists.org/fulldisclosure/2021/Mar/30
