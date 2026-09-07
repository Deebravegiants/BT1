# [M] field_test gem contains injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wg9m-gw3h-hg83
CVE: CVE-2019-13146
CWE: CWE-74
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-wg9m-gw3h-hg83
Type: github-advisory

## Affected
- RubyGems: `field_test` — affected >=0.3.0 <0.3.1

## Details
The field_test gem 0.3.0 for Ruby has unvalidated input. A method call that is expected to return a value from a certain set of inputs can be made to return any input, which can be dangerous depending on how applications use it. If an application treats arbitrary variants as trusted, this can lead to a variety of potential vulnerabilities like SQL injection or cross-site scripting (XSS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13146
- https://github.com/ankane/field_test/issues/17
- https://github.com/ankane/field_test
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/field_test/CVE-2019-13146.yml
- https://web.archive.org/web/20210115194802/http://www.securityfocus.com/bid/109114
