# [H] Arabic Prawn allows remote attackers to execute arbitrary commands via shell metacharacters

## Summary
Severity: High
Advisory: GHSA-hgmw-x865-hf9x
CVE: CVE-2014-2322
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-hgmw-x865-hf9x
Type: github-advisory

## Affected
- RubyGems: `Arabic-Prawn` — affected >=0

## Details
`lib/string_utf_support.rb` in the Arabic Prawn 0.0.1 gem for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in the (1) downloaded_file or (2) url variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2322
- https://github.com/ozeron/prawn-arabic
- https://web.archive.org/web/20160306235714/http://www.vapid.dhs.org/advisories/arabic-ruby-gem.html
- http://www.openwall.com/lists/oss-security/2014/03/10/8
- http://www.openwall.com/lists/oss-security/2014/03/12/6
