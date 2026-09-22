# [H] OS Command Injection in MiniMagick

## Summary
Severity: High
Advisory: GHSA-r7j3-vvh2-xrpj
CVE: CVE-2019-13574
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-18
Source: https://github.com/advisories/GHSA-r7j3-vvh2-xrpj
Type: github-advisory

## Affected
- RubyGems: `mini_magick` — affected >=0 <4.9.4

## Details
In `lib/mini_magick/image.rb` in MiniMagick before 4.9.4, a fetched remote image filename could cause remote command execution because `Image.open` input is directly passed to `Kernel#open`, which accepts a `|` character followed by a command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13574
- https://github.com/minimagick/minimagick/commit/4cd5081e58810d3394d27a67219e8e4e0445d851
- https://benjamin-bouchet.com/blog/vulnerabilite-dans-la-gem-mini_magick-version-4-9-4
- https://github.com/minimagick/minimagick
- https://github.com/minimagick/minimagick/compare/d484786...293f9bb
- https://github.com/minimagick/minimagick/releases/tag/v4.9.4
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mini_magick/CVE-2019-13574.yml
- https://lists.debian.org/debian-lts-announce/2019/10/msg00007.html
- https://seclists.org/bugtraq/2019/Jul/20
- https://www.debian.org/security/2019/dsa-4481
