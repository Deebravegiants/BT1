# [M] update_by_case before 0.1.3 can be vulnerable to sql injection

## Summary
Severity: Medium
Advisory: GHSA-33wh-w4m7-c6r8
CVE: CVE-2022-35956
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-08-11
Source: https://github.com/advisories/GHSA-33wh-w4m7-c6r8
Type: github-advisory

## Affected
- RubyGems: `update_by_case` — affected >=0 <0.1.3

## Details
Before version 0.1.3 `update_by_case` gem used custom sql strings, and it was not sanitized, making it vulnerable to sql injection. Upgrade to version >= 0.1.3 that uses `Arel` instead to construct the resulting sql statement, with sanitized sql.

## References
- https://github.com/camilova/activerecord-update-by-case/security/advisories/GHSA-33wh-w4m7-c6r8
- https://nvd.nist.gov/vuln/detail/CVE-2022-35956
- https://github.com/camilova/activerecord-update-by-case
- https://github.com/camilova/activerecord-update-by-case/releases/tag/v0.1.3-stable
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/update_by_case/CVE-2022-35956.yml
