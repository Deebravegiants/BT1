# [M] ldoce Gem Arbitrary Command Execution

## Summary
Severity: Medium
Advisory: GHSA-g266-3crh-h7gj
CVE: CVE-2013-1911
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-g266-3crh-h7gj
Type: github-advisory

## Affected
- RubyGems: `ldoce` — affected >=0

## Details
`lib/ldoce/word.rb` in the ldoce 0.0.2 gem for Ruby allows remote attackers to execute arbitrary commands via shell metacharacters in (1) an mp3 URL or (2) file name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1911
- https://github.com/markburns/ldoce/issues/1
- https://exchange.xforce.ibmcloud.com/vulnerabilities/83163
- https://github.com/markburns/ldoce
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ldoce/CVE-2013-1911.yml
- https://web.archive.org/web/20200229102422/http://www.securityfocus.com/bid/58783
- http://archives.neohapsis.com/archives/bugtraq/2013-04/0010.html
- http://otiose.dhs.org/advisories/ldoce-0.0.2-cmd-exec.html
- http://www.openwall.com/lists/oss-security/2013/03/31/3
- http://www.securityfocus.com/bid/58783
