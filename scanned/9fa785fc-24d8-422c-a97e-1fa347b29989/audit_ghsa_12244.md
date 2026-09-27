# [H] High severity vulnerability that affects thin

## Summary
Severity: High
Advisory: GHSA-j24p-r6wx-r79w
CVE: CVE-2009-3287
CWE: CWE-20
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-j24p-r6wx-r79w
Type: github-advisory

## Affected
- RubyGems: `thin` — affected >=0 <1.2.4

## Details
lib/thin/connection.rb in Thin web server before 1.2.4 relies on the X-Forwarded-For header to determine the IP address of the client, which allows remote attackers to spoof the IP address and hide activities via a modified X-Forwarded-For header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-3287
- https://github.com/advisories/GHSA-j24p-r6wx-r79w
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/thin/CVE-2009-3287.yml
- http://github.com/macournoyer/thin
- http://github.com/macournoyer/thin/blob/master/CHANGELOG
- http://github.com/macournoyer/thin/commit/7bd027914c5ffd36bb408ef47dc749de3b6e063a
- http://www.openwall.com/lists/oss-security/2009/09/12/1
