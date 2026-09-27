# [H] Sounder Contains Arbitrary Command Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-rfmf-rx8w-935w
CVE: CVE-2013-5647
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-rfmf-rx8w-935w
Type: github-advisory

## Affected
- RubyGems: `sounder` — affected >=0 <1.0.2

## Details
lib/sounder/sound.rb in the sounder gem 1.0.1 for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in a filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5647
- https://github.com/adamzaninovich/sounder
- https://github.com/adamzaninovich/sounder/blob/v1.0.1/lib/sounder/sound.rb
- https://github.com/advisories/GHSA-rfmf-rx8w-935w
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sounder/CVE-2013-5647.yml
- http://vapid.dhs.org/advisories/sounder-ruby-gem-cmd-inj.html
