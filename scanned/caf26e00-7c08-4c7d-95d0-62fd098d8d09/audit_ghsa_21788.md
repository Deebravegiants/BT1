# [M] Hub Package Arbitrary File Overwrite

## Summary
Severity: Medium
Advisory: GHSA-x5m6-jh4r-34mv
CVE: CVE-2014-0177
CWE: CWE-377
Ecosystem: Go, RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-x5m6-jh4r-34mv
Type: github-advisory

## Affected
- Go: `github.com/github/hub` — affected >=0 <1.12.1
- RubyGems: `hub` — affected >=0 <1.12.1

## Details
The `am` function in `lib/hub/commands.rb` in hub before 1.12.1 allows local users to overwrite arbitrary files via a symlink attack on a temporary patch file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0177
- https://github.com/github/hub/commit/016ec99d25b1cb83cb4367e541177aa431beb600
- https://github.com/mislav/hub/commit/016ec99d25b1cb83cb4367e541177aa431beb600
- https://github.com/mislav/hub
- https://github.com/mislav/hub/releases/tag/v1.12.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/hub/CVE-2014-0177.yml
