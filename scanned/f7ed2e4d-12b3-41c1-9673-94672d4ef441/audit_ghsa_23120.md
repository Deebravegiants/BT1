# [H] open-uri-cached Gem for Ruby Unsafe Temporary File Creation Enables Code Execution

## Summary
Severity: High
Advisory: GHSA-7m2w-9gw7-c3xp
CVE: CVE-2015-3649
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7m2w-9gw7-c3xp
Type: github-advisory

## Affected
- RubyGems: `open-uri-cached` — affected >=0

## Details
The open-uri-cached rubygem allows local users to execute arbitrary Ruby code by creating a directory under /tmp containing "openuri-" followed by a crafted UID, and putting Ruby code in said directory once a metafile is created.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3649
- https://github.com/tigris/open-uri-cached/issues/8
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/open-uri-cached/CVE-2015-3649.yml
- https://github.com/tigris/open-uri-cached
- https://github.com/tigris/open-uri-cached/blob/master/lib/open-uri/cached.rb
- https://web.archive.org/web/20210119122105/http://www.securityfocus.com/bid/74469
- http://seclists.org/oss-sec/2015/q2/373
- http://www.benjaminfleischer.com/2013/03/20/yaml-and-security-in-ruby
- http://www.openwall.com/lists/oss-security/2015/05/06/2
