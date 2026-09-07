# [M] Cross-site Scripting vulnerability in i18n translations helper method

## Summary
Severity: Medium
Advisory: GHSA-xxr8-833v-c7wc
CVE: CVE-2011-4319
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-xxr8-833v-c7wc
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=3.0.0 <3.0.11
- RubyGems: `actionpack` — affected >=3.1.0 <3.1.2

## Details
Cross-site scripting (XSS) vulnerability in the i18n translations helper method in Ruby on Rails 3.0.x before 3.0.11 and 3.1.x before 3.1.2, and the rails_xss plugin in Ruby on Rails 2.3.x, allows remote attackers to inject arbitrary web script or HTML via vectors related to a translations string whose name ends with an "html" substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4319
- https://github.com/rails/rails/commit/2d5b105d4bcb652550dda8b5613376d1b8beb70c
- https://github.com/rails/rails/commit/ba2d85012088fd0db0fab98b2e512c77c83cbade
- https://exchange.xforce.ibmcloud.com/vulnerabilities/71364
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2011-4319.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/K2HXD7c8fMU
- https://web.archive.org/web/20200228155840/http://www.securityfocus.com/bid/50722
- https://web.archive.org/web/20210307005941/http://www.securitytracker.com/id?1026342
- http://groups.google.com/group/rubyonrails-security/browse_thread/thread/2b61d70fb73c7cc5?pli=1
- http://groups.google.com/group/rubyonrails-security/msg/c65c24fbc4b6dd82?dmode=source&output=gplain
- http://openwall.com/lists/oss-security/2011/11/18/8
- http://weblog.rubyonrails.org/2011/11/18/rails-3-0-11-has-been-released
- http://weblog.rubyonrails.org/2011/11/18/rails-3-1-2-has-been-released
