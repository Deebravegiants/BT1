# [H] mixlib-archive Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-98wx-cw86-c97x
CVE: CVE-2017-1000026
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-98wx-cw86-c97x
Type: github-advisory

## Affected
- RubyGems: `mixlib-archive` — affected >=0 <0.4.0

## Details
Chef Software's mixlib-archive versions 0.3.0 and older are vulnerable to a directory traversal attack allowing attackers to overwrite arbitrary files by using `..` in tar archive entries

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000026
- https://github.com/chef/mixlib-archive/pull/6
- https://github.com/chef/mixlib-archive
- https://github.com/chef/mixlib-archive/blob/master/CHANGELOG.md
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mixlib-archive/CVE-2017-1000026.yml
