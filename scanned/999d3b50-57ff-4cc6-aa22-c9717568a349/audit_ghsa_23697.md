# [C] Active Record component in Ruby on Rails has a data-type injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-f57c-hx33-hvh8
CVE: CVE-2013-3221
CWE: CWE-20, CWE-89
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f57c-hx33-hvh8
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=0 <4.2.0

## Details
The Active Record component in Ruby on Rails 2.3.x, 3.0.x, 3.1.x, and 3.2.x does not ensure that the declared data type of a database column is used during comparisons of input values to stored values in that column, which makes it easier for remote attackers to conduct data-type injection attacks against Ruby on Rails applications via a crafted value, as demonstrated by unintended interaction between the "typed XML" feature and a MySQL database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-3221
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2013-3221.yml
- https://groups.google.com/group/rubyonrails-security/msg/1f3bc0b88a60c1ce?dmode=source&output=gplain
- https://web.archive.org/web/20130825191249/http://www.phenoelit.org/blog/archives/2013/02/index.html
- http://openwall.com/lists/oss-security/2013/02/06/7
- http://openwall.com/lists/oss-security/2013/04/24/7
- http://pl.reddit.com/r/netsec/comments/17yajp/mysql_madness_and_rails
