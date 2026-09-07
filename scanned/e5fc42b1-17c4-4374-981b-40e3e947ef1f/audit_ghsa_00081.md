# [C] rest-client Gem Vulnerable to Session Fixation

## Summary
Severity: Critical
Advisory: GHSA-3fhf-6939-qg8p
CVE: CVE-2015-1820
CWE: CWE-384
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-13
Source: https://github.com/advisories/GHSA-3fhf-6939-qg8p
Type: github-advisory

## Affected
- RubyGems: `rest-client` — affected >=1.6.1.a <1.8.0

## Details
REST client for Ruby (aka rest-client) versions 1.6.1.a until 1.8.0 allow remote attackers to conduct session fixation attacks or obtain sensitive cookie information by leveraging passage of cookies set in a response to a redirect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1820
- https://github.com/rest-client/rest-client/issues/369
- https://bugzilla.redhat.com/show_bug.cgi?id=1205291
- https://github.com/rest-client/rest-client
- https://rubygems.org/gems/rest-client/versions/1.6.1.a
- https://web.archive.org/web/20200228080106/http://www.securityfocus.com/bid/73295
- http://www.openwall.com/lists/oss-security/2015/03/24/3
