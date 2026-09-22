# [C] BibTeX-Ruby vulnerable to OS command injection

## Summary
Severity: Critical
Advisory: GHSA-c5r5-7pfh-6qg6
CVE: CVE-2019-10780
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-14
Source: https://github.com/advisories/GHSA-c5r5-7pfh-6qg6
Type: github-advisory

## Affected
- RubyGems: `bibtex-ruby` — affected >=0 <5.1.0

## Details
BibTeX-ruby before 5.1.0 allows shell command injection due to unsanitized user input being passed directly to the built-in Ruby `Kernel.open` method through BibTeX.open.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10780
- https://github.com/inukshuk/bibtex-ruby/commit/14406f4460f4e1ecabd25ca94f809b3ea7c5fb11
- https://github.com/advisories/GHSA-c5r5-7pfh-6qg6
- https://github.com/inukshuk/bibtex-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bibtex-ruby/CVE-2019-10780.yml
- https://snyk.io/vuln/SNYK-RUBY-BIBTEXRUBY-542602
