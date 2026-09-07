# [H] Shell command injection in command_wrap

## Summary
Severity: High
Advisory: GHSA-p673-hjf2-pwfr
CVE: CVE-2013-1875
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-p673-hjf2-pwfr
Type: github-advisory

## Affected
- RubyGems: `command_wrap` — affected >=0

## Details
command_wrap.rb in the command_wrap Gem for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in a URL or filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1875
- https://github.com/advisories/GHSA-p673-hjf2-pwfr
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/command_wrap/CVE-2013-1875.yml
- https://github.com/slicertje/commandwrap
- http://packetstormsecurity.com/files/120847/Ruby-Gem-Command-Wrap-Command-Execution.html
- http://seclists.org/fulldisclosure/2013/Mar/175
- http://www.openwall.com/lists/oss-security/2013/03/19/9
