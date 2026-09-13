# [H] sprout Arbitrary Code Execution vulnerability

## Summary
Severity: High
Advisory: GHSA-229r-pqp6-8w6g
CVE: CVE-2013-6421
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-229r-pqp6-8w6g
Type: github-advisory

## Affected
- RubyGems: `sprout` — affected 0.7.246

## Details
The `unpack_zip` function in `archive_unpacker.rb` in the sprout gem 0.7.246 for Ruby allows context-dependent attackers to execute arbitrary commands via shell metacharacters in a (1) filename or (2) path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6421
- https://github.com/lukebayes/project-sprouts
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sprout/CVE-2013-6421.yml
- http://archives.neohapsis.com/archives/bugtraq/2013-12/0077.html
- http://vapid.dhs.org/advisories/sprout-0.7.246-command-inj.html
- http://www.openwall.com/lists/oss-security/2013/12/03/1
- http://www.openwall.com/lists/oss-security/2013/12/03/6
