# [M] paperclip Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6jvm-3j5h-79f6
CVE: CVE-2015-2963
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-6jvm-3j5h-79f6
Type: github-advisory

## Affected
- RubyGems: `paperclip` — affected >=0 <4.2.2

## Details
The thoughtbot paperclip gem before 4.2.2 for Ruby does not consider the content-type value during media-type validation, which allows remote attackers to upload HTML documents and conduct cross-site scripting (XSS) attacks via a spoofed value, as demonstrated by image/jpeg.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2963
- https://github.com/thoughtbot/paperclip/commit/9aee4112f36058cd28d5fe4a006d6981bd1eda57
- https://github.com/thoughtbot/paperclip
- https://robots.thoughtbot.com/paperclip-security-release
- https://web.archive.org/web/20200228084907/http://www.securityfocus.com/bid/75304
- http://jvn.jp/en/jp/JVN83881261/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2015-000088
- http://openwall.com/lists/oss-security/2015/06/19/3
