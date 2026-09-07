# [H] sfpagent Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-vm28-mrm7-fpjq
CVE: CVE-2014-2888
CWE: CWE-77
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-vm28-mrm7-fpjq
Type: github-advisory

## Affected
- RubyGems: `sfpagent` — affected >=0 <0.4.15

## Details
`lib/sfpagent/bsig.rb` in the sfpagent gem before 0.4.15 for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in the module name in a JSON request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2888
- https://github.com/herry13/sfpagent
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sfpagent/CVE-2014-2888.yml
- https://web.archive.org/web/20201029141944/http://www.vapid.dhs.org/advisories/spfagent-remotecmd.html
- http://seclists.org/fulldisclosure/2014/Apr/243
- http://www.openwall.com/lists/oss-security/2014/04/16/1
- http://www.openwall.com/lists/oss-security/2014/04/18/4
