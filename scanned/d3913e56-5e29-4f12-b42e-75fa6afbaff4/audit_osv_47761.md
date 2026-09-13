# [H] CVE-2017-11556

## Summary
Severity: High
Advisory: CVE-2017-11556
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-23
Source: https://osv.dev/vulnerability/CVE-2017-11556
Type: osv

## Details
There is a stack consumption vulnerability in the Parser::advanceToNextToken function in parser.cpp in LibSass 3.4.5. A crafted input may lead to remote denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1471786
