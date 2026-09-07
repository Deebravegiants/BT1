# [H] Sort order SQL injection in Administrate

## Summary
Severity: High
Advisory: GHSA-2p5p-m353-833w
CVE: CVE-2020-5257
CWE: CWE-943
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-03-13
Source: https://github.com/advisories/GHSA-2p5p-m353-833w
Type: github-advisory

## Affected
- RubyGems: `administrate` — affected >=0 <0.13.0

## Details
In Administrate (rubygem) before version 0.13.0, when sorting by attributes on a dashboard,
the direction parameter was not validated before being interpolated into the SQL query.
This could present a SQL injection if the attacker were able to modify the `direction` parameter and bypass ActiveRecord SQL protections.

Whilst this does have a high-impact, to exploit this you need access to the Administrate dashboards, which we would expect to be behind authentication.

This is patched in wersion 0.13.0.

## References
- https://github.com/thoughtbot/administrate/security/advisories/GHSA-2p5p-m353-833w
- https://nvd.nist.gov/vuln/detail/CVE-2020-5257
- https://github.com/thoughtbot/administrate/commit/3ab838b83c5f565fba50e0c6f66fe4517f98eed3
- https://github.com/advisories/GHSA-2p5p-m353-833w
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/administrate/CVE-2020-5257.yml
