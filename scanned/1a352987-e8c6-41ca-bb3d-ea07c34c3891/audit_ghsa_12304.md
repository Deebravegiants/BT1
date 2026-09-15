# [C] Doorkeeper is vulnerable to replay attacks

## Summary
Severity: Critical
Advisory: GHSA-3m6r-39p3-jq25
CVE: CVE-2016-6582
CWE: CWE-1254
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-3m6r-39p3-jq25
Type: github-advisory

## Affected
- RubyGems: `doorkeeper` — affected >=0 <4.2.0

## Details
The Doorkeeper gem before 4.2.0 for Ruby might allow remote attackers to conduct replay attacks or revoke arbitrary tokens by leveraging failure to implement the OAuth 2.0 Token Revocation specification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6582
- https://github.com/doorkeeper-gem/doorkeeper/issues/875
- https://github.com/advisories/GHSA-3m6r-39p3-jq25
- https://github.com/doorkeeper-gem/doorkeeper
- https://github.com/doorkeeper-gem/doorkeeper/releases/tag/v4.2.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/doorkeeper/CVE-2016-6582.yml
- https://web.archive.org/web/20170214021758/http://www.securityfocus.com/bid/92551
- https://web.archive.org/web/20201207202519/http://www.securityfocus.com/archive/1/539268/100/0/threaded
- http://packetstormsecurity.com/files/138430/Doorkeeper-4.1.0-Token-Revocation.html
- http://seclists.org/fulldisclosure/2016/Aug/105
- http://www.openwall.com/lists/oss-security/2016/08/19/2
