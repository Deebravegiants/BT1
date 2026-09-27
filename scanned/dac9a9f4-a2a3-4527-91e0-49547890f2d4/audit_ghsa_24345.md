# [H] Echor contains Command Injection

## Summary
Severity: High
Advisory: GHSA-8936-cgj4-phr2
CVE: CVE-2014-1834
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8936-cgj4-phr2
Type: github-advisory

## Affected
- RubyGems: `echor` — affected >=0

## Details
The `perform_request` function in `/lib/echor/backplane.rb` in echor 0.1.6 Ruby Gem allows local users to inject arbitrary code by adding a semi-colon in their username or password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1834
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/echor/CVE-2014-1834.yml
- http://www.openwall.com/lists/oss-security/2014/01/31/10
