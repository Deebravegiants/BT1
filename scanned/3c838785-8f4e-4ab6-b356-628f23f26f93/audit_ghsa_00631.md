# [M] http vulnerable to Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-6wpv-cj6x-v3jw
CVE: CVE-2015-1828
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-03-13
Source: https://github.com/advisories/GHSA-6wpv-cj6x-v3jw
Type: github-advisory

## Affected
- RubyGems: `http` — affected >=0.7.0 <0.7.3
- RubyGems: `http` — affected >=0 <0.6.4

## Details
The Ruby http gem before 0.6.4 and 0.7.3 does not verify hostnames in SSL connections, which might allow remote attackers to obtain sensitive information via a man-in-the-middle-attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1828
- https://github.com/ruby/openssl/issues/8
- https://github.com/httprb/http
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/http/CVE-2015-1828.yml
- https://groups.google.com/forum/#!topic/httprb/jkb4oxwZjkU
- https://my.diffend.io/gems/http/0.6.3/0.6.4
- https://my.diffend.io/gems/http/0.7.2/0.7.3
- https://rubysec.com/advisories/http-CVE-2015-1828
