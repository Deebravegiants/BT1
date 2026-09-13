# [M] rack-protection gem timing attack vulnerability when validating CSRF token

## Summary
Severity: Medium
Advisory: GHSA-688c-3x49-6rqj
CVE: CVE-2018-1000119
CWE: CWE-203
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-03-07
Source: https://github.com/advisories/GHSA-688c-3x49-6rqj
Type: github-advisory

## Affected
- RubyGems: `rack-protection` — affected >=0 <1.5.5
- RubyGems: `rack-protection` — affected >=2.0.0.beta1 <2.0.0

## Details
Sinatra rack-protection versions 1.5.4 and 2.0.0.rc3 and earlier contains a timing attack vulnerability in the CSRF token checking that can result in signatures can be exposed. This attack appear to be exploitable via network connectivity to the ruby application. This vulnerability appears to have been fixed in 1.5.5 and 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000119
- https://github.com/sinatra/rack-protection/pull/98
- https://github.com/sinatra/sinatra/commit/8aa6c42ef724f93ae309fb7c5668e19ad547eceb#commitcomment-27964109
- https://access.redhat.com/errata/RHSA-2018:1060
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack-protection/CVE-2018-1000119.yml
- https://github.com/sinatra/rack-protection
- https://www.debian.org/security/2018/dsa-4247
