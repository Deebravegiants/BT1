# [M] Exposure of Sensitive Information in bio-basespace-sdk

## Summary
Severity: Medium
Advisory: GHSA-xwr3-fmgj-mmfr
CVE: CVE-2013-7111
CWE: CWE-200
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-xwr3-fmgj-mmfr
Type: github-advisory

## Affected
- RubyGems: `bio-basespace-sdk` — affected >=0

## Details
The put_call function in the API client (`api/api_client.rb`) in the BaseSpace Ruby SDK (aka bio-basespace-sdk) gem 0.1.7 for Ruby uses the `API_KEY` on the command line, which allows remote attackers to obtain sensitive information by listing the processes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7111
- https://github.com/advisories/GHSA-xwr3-fmgj-mmfr
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bio-basespace-sdk/CVE-2013-7111.yml
- http://www.openwall.com/lists/oss-security/2013/12/14/2
- http://www.openwall.com/lists/oss-security/2013/12/15/5
- http://www.vapid.dhs.org/advisories/bio-basespace-sdk.html
