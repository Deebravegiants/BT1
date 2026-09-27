# [H] rswag vulnerable to arbitrary JSON and YAML file read via directory traversal

## Summary
Severity: High
Advisory: GHSA-vc79-65pr-q82v
CVE: CVE-2023-38337
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-15
Source: https://github.com/advisories/GHSA-vc79-65pr-q82v
Type: github-advisory

## Affected
- RubyGems: `rswag` — affected >=0 <2.10.1

## Details
rswag before 2.10.1 allows remote attackers to read arbitrary JSON and YAML files via directory traversal, because rswag-api can expose a file that is not the OpenAPI (or Swagger) specification file of a project.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38337
- https://github.com/rswag/rswag/issues/653
- https://github.com/rswag/rswag
- https://github.com/rswag/rswag/compare/2.9.0...2.10.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rswag/CVE-2023-38337.yml
