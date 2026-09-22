# [H] CVE-2017-6181

## Summary
Severity: High
Advisory: CVE-2017-6181
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2017-6181
Type: osv

## Details
The parse_char_class function in regparse.c in the Onigmo (aka Oniguruma-mod) regular expression library, as used in Ruby 2.4.0, allows remote attackers to cause a denial of service (deep recursion and application crash) via a crafted regular expression.

## References
- http://www.securityfocus.com/bid/97304
- https://bugs.ruby-lang.org/issues/13234
- https://bugs.ruby-lang.org/projects/ruby-trunk/repository/revisions/57660
