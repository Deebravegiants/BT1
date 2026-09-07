# [C] qcubed PHP object injection

## Summary
Severity: Critical
Advisory: GHSA-7w3c-jgh7-cwjw
CVE: CVE-2020-24914
CWE: CWE-915
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7w3c-jgh7-cwjw
Type: github-advisory

## Affected
- Packagist: `qcubed/qcubed` — affected >=0 <3.2

## Details
A PHP object injection bug in profile.php in qcubed (all versions including 3.1.1) unserializes the untrusted data of the POST-variable "strProfileData" and allows an unauthenticated attacker to execute code via a crafted POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24914
- https://github.com/qcubed/qcubed/pull/1320/files
- https://github.com/qcubed/qcubed
- https://tech.feedyourhead.at/content/QCubed-PHP-Object-Injection-CVE-2020-24914
- https://www.ait.ac.at/themen/cyber-security/pentesting/security-advisories/ait-sa-20210215-01
- http://qcubed.com
- http://seclists.org/fulldisclosure/2021/Mar/28
