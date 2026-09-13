# [C] strong_password Ruby gem malicious version causing Remote Code Execution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5h5r-ffc4-c455
CVE: CVE-2019-13354
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-08
Source: https://github.com/advisories/GHSA-5h5r-ffc4-c455
Type: github-advisory

## Affected
- RubyGems: `strong_password` — affected >=0.0.7 <0.0.8

## Details
The strong_password gem 0.0.7 for Ruby, as distributed on RubyGems.org, included a code-execution backdoor inserted by a third party. Version 0.0.8 does not contain the backdoor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13354
- https://benjamin-bouchet.com/blog/vulnerabilite-dans-la-gem-strong_password-0-0-7
- https://github.com/bdmac/strong_password
- https://github.com/bdmac/strong_password/releases
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/strong_password/CVE-2019-13354.yml
- https://rubygems.org/gems/strong_password/versions
- https://withatwist.dev/strong-password-rubygem-hijacked.html
