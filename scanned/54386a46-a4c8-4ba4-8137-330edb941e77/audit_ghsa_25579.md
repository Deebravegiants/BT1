# [C] SQL injection in pagekit/pagekit

## Summary
Severity: Critical
Advisory: GHSA-45hc-r4fj-qj89
CVE: CVE-2021-44135
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-02
Source: https://github.com/advisories/GHSA-45hc-r4fj-qj89
Type: github-advisory

## Affected
- Packagist: `pagekit/pagekit` — affected >=0

## Details
Pagekit is a modular and lightweight CMS built with Symfony components and Vue.js. The configAction in SettingsController allow user to set the order of comments listing. The allowed options are ASC and DESC. That config then get concatenated directly to the SQL query. Due to the fact that there wasnt any sanitizion before saving that config, it can lead to the SQL Injection vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44135
- https://github.com/pagekit/pagekit
- https://huntr.dev/bounties/82f09b08-ceeb-4249-8855-b8bc718c4868
