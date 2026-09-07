# [H] MunkiReport reportdata module SQL injection vulnerability

## Summary
Severity: High
Advisory: GHSA-qvw9-6567-wq78
CVE: CVE-2020-15886
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qvw9-6567-wq78
Type: github-advisory

## Affected
- Packagist: `munkireport/reportdata` — affected >=0 <3.5

## Details
A SQL injection vulnerability in reportdata_controller.php in the reportdata module before 3.5 for MunkiReport allows attackers to execute arbitrary SQL commands via the req parameter of the /module/reportdata/ip endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15886
- https://github.com/munkireport/munkireport-php/releases
- https://github.com/munkireport/munkireport-php/releases/tag/v5.6.3
- https://github.com/munkireport/munkireport-php/wiki/20200722-SQL-Injection-In-Reportdata-Ip-In-'req'-GET-Parameter
- https://github.com/munkireport/reportdata
- https://github.com/munkireport/reportdata/releases
