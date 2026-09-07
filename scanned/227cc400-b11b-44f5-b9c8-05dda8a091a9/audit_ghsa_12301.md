# [M] rack-ssl Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v3rr-cph9-2g2q
CVE: CVE-2014-2538
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-v3rr-cph9-2g2q
Type: github-advisory

## Affected
- RubyGems: `rack-ssl` — affected >=0 <1.4.0

## Details
Cross-site scripting (XSS) vulnerability in `lib/rack/ssl.rb` in the rack-ssl gem before 1.4.0 for Ruby allows remote attackers to inject arbitrary web script or HTML via a URI, which might not be properly handled by third-party adapters such as JRuby-Rack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2538
- https://github.com/josh/rack-ssl/commit/9d7d7300b907e496db68d89d07fbc2e0df0b487b
- https://github.com/josh/rack-ssl
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack-ssl/CVE-2014-2538.yml
- https://web.archive.org/web/20140524002455/http://secunia.com/advisories/57466
- https://web.archive.org/web/20200228185649/http://www.securityfocus.com/bid/66314
- http://lists.opensuse.org/opensuse-updates/2014-04/msg00032.html
- http://www.openwall.com/lists/oss-security/2014/03/19/20
