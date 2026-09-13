# [H] yajl-ruby gem Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-wwh7-4jw9-33x6
CVE: CVE-2017-16516
CWE: CWE-134
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-11-28
Source: https://github.com/advisories/GHSA-wwh7-4jw9-33x6
Type: github-advisory

## Affected
- RubyGems: `yajl-ruby` — affected >=0 <1.3.1

## Details
In the yajl-ruby gem 1.3.0 for Ruby, when a crafted JSON file is supplied to `Yajl::Parser.new.parse`, the whole ruby process crashes with a SIGABRT in the `yajl_string_decode` function in `yajl_encode.c`. This results in the whole ruby process terminating and potentially a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16516
- https://github.com/brianmario/yajl-ruby/issues/176
- https://github.com/brianmario/yajl-ruby/pull/178
- https://github.com/github/advisory-database/pull/2158
- https://github.com/brianmario/yajl-ruby/commit/a8ca8f476655adaa187eedc60bdc770fff3c51ce
- https://github.com/brianmario/yajl-ruby
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/yajl-ruby/CVE-2017-16516.yml
- https://lists.debian.org/debian-lts-announce/2017/11/msg00010.html
- https://lists.debian.org/debian-lts-announce/2023/07/msg00013.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00003.html
- https://rubygems.org/gems/yajl-ruby
