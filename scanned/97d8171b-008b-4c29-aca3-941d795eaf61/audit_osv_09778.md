# [C] CVE-2017-11465

## Summary
Severity: Critical
Advisory: CVE-2017-11465
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-19
Source: https://osv.dev/vulnerability/CVE-2017-11465
Type: osv

## Details
The parser_yyerror function in the UTF-8 parser in Ruby 2.4.1 allows attackers to cause a denial of service (invalid write or read) or possibly have unspecified other impact via a crafted Ruby script, related to the parser_tokadd_utf8 function in parse.y. NOTE: this might have security relevance as a bypass of a $SAFE protection mechanism.

## References
- https://bugs.ruby-lang.org/issues/13742
- https://bugs.ruby-lang.org/projects/ruby-trunk/repository/revisions/59344
