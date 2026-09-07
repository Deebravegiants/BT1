# [C] Bacula-web SQL Injection Vulnerabilities

## Summary
Severity: Critical
Advisory: GHSA-fv4m-5j2c-787r
CVE: CVE-2017-15367
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-fv4m-5j2c-787r
Type: github-advisory

## Affected
- Packagist: `bacula-web/bacula-web` — affected >=0 <8.0.0-rc2

## Details
Bacula-web before 8.0.0-rc2 is affected by multiple SQL Injection vulnerabilities that could allow an attacker to access the Bacula database and, depending on configuration, escalate privileges on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15367
- https://github.com/bacula-web/bacula-web/commit/90d4c44a0dd0d65c6fb3ab2417b83d700c8413ae
- https://github.com/bacula-web/bacula-web
- https://web.archive.org/web/20180324124226/http://bacula-web.org/download/articles/bacula-web-8-0-0-rc2.html
- https://web.archive.org/web/20180625090858/http://bugs.bacula-web.org/view.php?id=211
- https://www.exploit-db.com/exploits/44272
