# [C] espeak-ruby allows arbitrary command execution

## Summary
Severity: Critical
Advisory: GHSA-4jm3-pfpf-h54p
CVE: CVE-2016-10193
CWE: CWE-284
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-4jm3-pfpf-h54p
Type: github-advisory

## Affected
- RubyGems: `espeak-ruby` — affected >=0 <1.0.3

## Details
The espeak-ruby gem before 1.0.3 for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in a string to the `speak`, `save`, `bytes` or `bytes_wav` method in `lib/espeak/speech.rb`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10193
- https://github.com/dejan/espeak-ruby/issues/7
- https://github.com/dejan/espeak-ruby/commit/5251744b13bdd9fb0c72c612226e72d330bac143
- https://github.com/dejan/espeak-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/espeak-ruby/CVE-2016-10193.yml
- http://www.openwall.com/lists/oss-security/2017/01/31/14
- http://www.openwall.com/lists/oss-security/2017/02/02/5
