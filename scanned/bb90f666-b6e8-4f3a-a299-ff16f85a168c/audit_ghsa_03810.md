# [C] SQL Injection in marginalia

## Summary
Severity: Critical
Advisory: GHSA-hrj5-qp7x-rpg6
CVE: CVE-2019-1010191
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-26
Source: https://github.com/advisories/GHSA-hrj5-qp7x-rpg6
Type: github-advisory

## Affected
- RubyGems: `marginalia` — affected >=0 <1.6

## Details
marginalia < 1.6 is affected by SQL Injection. The impact is an injection of any SQL queries when a user controller argument is added as a component. This issue affects users that add a component that is user controller, for instance a parameter or a header. The attack vector is inputting of SQL to a vulnerable vector (header, http parameter, etc). The fixed version is 1.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010191
- https://github.com/basecamp/marginalia/pull/73
- https://github.com/basecamp/marginalia
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/marginalia/CVE-2019-1010191.yml
