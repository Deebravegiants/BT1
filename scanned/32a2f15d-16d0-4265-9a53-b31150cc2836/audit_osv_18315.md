# [C] CVE-2020-26045

## Summary
Severity: Critical
Advisory: CVE-2020-26045
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-05
Source: https://osv.dev/vulnerability/CVE-2020-26045
Type: osv

## Details
FUEL CMS 1.4.11 allows SQL Injection via parameter 'name' in /fuel/permissions/create/. Exploiting this issue could allow an attacker to compromise the application, access or modify data, or exploit latent vulnerabilities in the underlying database.

## References
- https://getfuelcms.com
- https://github.com/daylightstudio/FUEL-CMS/releases/tag/1.4.11
- https://github.com/daylightstudio/FUEL-CMS/issues/575
