# [M] Geminabox contains Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-653m-r33x-39ff
CVE: CVE-2017-16792
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-11-29
Source: https://github.com/advisories/GHSA-653m-r33x-39ff
Type: github-advisory

## Affected
- RubyGems: `geminabox` — affected >=0 <0.13.10

## Details
Stored cross-site scripting (XSS) vulnerability in "geminabox" (Gem in a Box) before 0.13.10 allows attackers to inject arbitrary web script via the "homepage" value of a ".gemspec" file, related to views/gem.erb and views/index.erb.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16792
- https://github.com/geminabox/geminabox/commit/f8429a9e364658459add170e4ebc7a5d3b4759e7
- https://github.com/geminabox/geminabox
- https://github.com/geminabox/geminabox/blob/master/CHANGELOG.md
- https://rubygems.org/gems/geminabox/versions/0.13.10
