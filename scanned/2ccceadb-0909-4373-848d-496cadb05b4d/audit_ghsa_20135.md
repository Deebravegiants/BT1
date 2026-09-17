# [H] Inefficient Regular Expression Complexity in rails-html-sanitizer

## Summary
Severity: High
Advisory: GHSA-5x79-w82f-gw8w
CVE: CVE-2022-23517
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-5x79-w82f-gw8w
Type: github-advisory

## Affected
- RubyGems: `rails-html-sanitizer` — affected >=0 <1.4.4

## Details
## Summary

Certain configurations of rails-html-sanitizer `< 1.4.4` use an inefficient regular expression that is susceptible to excessive backtracking when attempting to sanitize certain SVG attributes. This may lead to a denial of service through CPU resource consumption.


## Mitigation

Upgrade to rails-html-sanitizer `>= 1.4.4`.


## Severity

The maintainers have evaluated this as [High Severity 7.5 (CVSS3.1)](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H).


## References

- [CWE - CWE-1333: Inefficient Regular Expression Complexity (4.9)](https://cwe.mitre.org/data/definitions/1333.html)
- https://hackerone.com/reports/1684163


## Credit

This vulnerability was responsibly reported by @ooooooo-q (https://github.com/ooooooo-q).

## References
- https://github.com/rails/rails-html-sanitizer/security/advisories/GHSA-5x79-w82f-gw8w
- https://nvd.nist.gov/vuln/detail/CVE-2022-23517
- https://github.com/rails/rails-html-sanitizer/commit/56c61c0cebd1e493e8ad7bca2a0191609a4a6979
- https://hackerone.com/reports/1684163
- https://github.com/rails/rails-html-sanitizer
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails-html-sanitizer/CVE-2022-23517.yml
- https://lists.debian.org/debian-lts-announce/2023/09/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00045.html
