# [M] Ciborg gem for Ruby allows local users to write files and gain privileges via Symlink

## Summary
Severity: Medium
Advisory: GHSA-g982-9r8g-6qxw
CVE: CVE-2014-5003
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-g982-9r8g-6qxw
Type: github-advisory

## Affected
- RubyGems: `ciborg` — affected 3.0.0

## Details
There is a /tmp file race condition in `chef/travis-cookbooks/ci_environment/perlbrew/recipes/default.rb` in the ciborg gem 3.0.0 when creating `/tmp/perlbrew-installer`. If a malicious local user creates the file first they can overwrite the contents with their own code executing it as the ciborg process owner.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-5003
- https://github.com/advisories/GHSA-g982-9r8g-6qxw
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ciborg/CVE-2014-5003.yml
- http://www.openwall.com/lists/oss-security/2014/07/07/24
- http://www.openwall.com/lists/oss-security/2014/07/17/5
- http://www.vapid.dhs.org/advisories/ciborg-3.0.0.html
