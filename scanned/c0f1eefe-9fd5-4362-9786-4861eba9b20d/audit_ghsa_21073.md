# [H] opensearch-ruby 2.x before 2.0.2 vulnerable to unsafe YAML deserialization

## Summary
Severity: High
Advisory: GHSA-977c-63xq-cgw3
CVE: CVE-2022-31115
CWE: CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-05
Source: https://github.com/advisories/GHSA-977c-63xq-cgw3
Type: github-advisory

## Affected
- RubyGems: `opensearch-ruby` — affected >=2.0.0 <2.0.2

## Details
### Impact
A YAML deserialization in opensearch-ruby 2.0.0 can lead to unsafe deserialization using YAML.load if the response is of type YAML.

### Patches
The problem has been patched in opensearch-ruby gem version 2.0.2.

### Workarounds
No viable workaround.  Please upgrade to 2.0.2

### References
https://github.com/opensearch-project/opensearch-ruby/pull/77
https://staaldraad.github.io/post/2021-01-09-universal-rce-ruby-yaml-load-updated/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [opensearch-ruby](https://github.com/opensearch-project/opensearch-ruby)

## References
- https://github.com/opensearch-project/opensearch-ruby/security/advisories/GHSA-977c-63xq-cgw3
- https://nvd.nist.gov/vuln/detail/CVE-2022-31115
- https://github.com/opensearch-project/opensearch-ruby/pull/77
- https://github.com/opensearch-project/opensearch-ruby/commit/d74a98b45c037671e8819fa87f6a6423458ab08a
- https://github.com/opensearch-project/opensearch-ruby
- https://github.com/opensearch-project/opensearch-ruby/compare/v2.0.1...v2.0.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/opensearch-ruby/CVE-2022-31115.yml
- https://staaldraad.github.io/post/2021-01-09-universal-rce-ruby-yaml-load-updated
