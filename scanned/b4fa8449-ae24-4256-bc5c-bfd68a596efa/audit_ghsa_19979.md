# [M] Improper neutralization of data URIs may allow XSS in rails-html-sanitizer

## Summary
Severity: Medium
Advisory: GHSA-mcvf-2q2m-x72m
CVE: CVE-2022-23518
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-mcvf-2q2m-x72m
Type: github-advisory

## Affected
- RubyGems: `rails-html-sanitizer` — affected >=1.0.3 <1.4.4

## Details
## Summary

rails-html-sanitizer `>= 1.0.3, < 1.4.4` is vulnerable to cross-site scripting via data URIs when used in combination with Loofah `>= 2.1.0`.


## Mitigation

Upgrade to rails-html-sanitizer `>= 1.4.4`.


## Severity

The maintainers have evaluated this as [Medium Severity 6.1](https://www.first.org/cvss/calculator/3.0#CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N).


## References

- [CWE - CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') (4.9)](https://cwe.mitre.org/data/definitions/79.html)
- [SVG MIME Type (image/svg+xml) is misleading to developers · Issue #266 · w3c/svgwg](https://github.com/w3c/svgwg/issues/266)
- https://github.com/rails/rails-html-sanitizer/issues/135
- https://hackerone.com/reports/1694173


## Credit

This vulnerability was independently reported by Maciej Piechota (@haqpl) and Mrinmoy Das (@goromlagche).

## References
- https://github.com/rails/rails-html-sanitizer/security/advisories/GHSA-mcvf-2q2m-x72m
- https://nvd.nist.gov/vuln/detail/CVE-2022-23518
- https://github.com/rails/rails-html-sanitizer/issues/135
- https://github.com/w3c/svgwg/issues/266
- https://hackerone.com/reports/1694173
- https://github.com/rails/rails-html-sanitizer
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails-html-sanitizer/CVE-2022-23518.yml
- https://lists.debian.org/debian-lts-announce/2023/09/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00045.html
