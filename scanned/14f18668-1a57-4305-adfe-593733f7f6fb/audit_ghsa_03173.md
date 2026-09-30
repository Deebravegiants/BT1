# [H] Dependency Confusion in Bundler

## Summary
Severity: High
Advisory: GHSA-fp4w-jxhp-m23p
CVE: CVE-2020-36327
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-fp4w-jxhp-m23p
Type: github-advisory

## Affected
- RubyGems: `bundler` — affected >=1.16.0 <2.2.10
- RubyGems: `bundler` — affected >=2.2.11 <2.2.18

## Details
Bundler 1.16.0 through 2.2.9 and 2.2.11 through 2.2.17 sometimes chooses a dependency source based on the highest gem version number, which means that a rogue gem found at a public source may be chosen, even if the intended choice was a private gem that is a dependency of another private gem that is explicitly depended on by the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36327
- https://github.com/rubygems/rubygems/issues/3982
- https://github.com/rubygems/rubygems/pull/4609
- https://github.com/rubygems/rubygems/commit/078bf682ac40017b309b5fc69f283ff640e7c129
- https://bundler.io/blog/2021/02/15/a-more-secure-bundler-we-fixed-our-source-priorities.html
- https://github.com/rubygems/rubygems
- https://github.com/rubygems/rubygems/blob/master/bundler/CHANGELOG.md#2218-may-25-2021
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bundler/CVE-2020-36327.yml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MWXHK5UUHVSHF7HTHMX6JY3WXDVNIHSL
- https://mensfeld.pl/2021/02/rubygems-dependency-confusion-attack-side-of-things
- https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-24105
- https://www.zofrex.com/blog/2021/04/29/bundler-still-vulnerable-dependency-confusion-cve-2020-36327
