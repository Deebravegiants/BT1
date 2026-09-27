# [H] Curl Gem insufficient URL escaping command injection

## Summary
Severity: High
Advisory: GHSA-hxx6-p24v-wg8c
CVE: CVE-2013-2617
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-hxx6-p24v-wg8c
Type: github-advisory

## Affected
- RubyGems: `curl` — affected >=0

## Details
`lib/curl.rb` in the Curl Gem for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in a URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2617
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/curl/CVE-2013-2617.yml
- https://github.com/tggo/curl
- http://packetstormsecurity.com/files/120778/Ruby-Gem-Curl-Command-Execution.html
- http://seclists.org/fulldisclosure/2013/Mar/124
- http://www.openwall.com/lists/oss-security/2013/03/19/9
