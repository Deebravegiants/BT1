# [M] RedCloth Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r23g-3qw4-gfh2
CVE: CVE-2012-6684
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-r23g-3qw4-gfh2
Type: github-advisory

## Affected
- RubyGems: `RedCloth` — affected >=0 <4.3.0

## Details
Cross-site scripting (XSS) vulnerability in the RedCloth library 4.2.9 for Ruby and earlier allows remote attackers to inject arbitrary web script or HTML via a `javascript:` URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6684
- https://co3k.org/blog/redcloth-unfixed-xss-en
- https://gist.github.com/co3k/75b3cb416c342aa1414c
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/RedCloth/CVE-2012-6684.yml
- https://web.archive.org/web/20150128115714/http://jgarber.lighthouseapp.com/projects/13054-redcloth/tickets/243-xss
- http://seclists.org/fulldisclosure/2014/Dec/50
- http://www.debian.org/security/2015/dsa-3168
