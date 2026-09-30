# [M] CVE-2017-11608

## Summary
Severity: Medium
Advisory: CVE-2017-11608
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-24
Source: https://osv.dev/vulnerability/CVE-2017-11608
Type: osv

## Details
There is a heap-based buffer over-read in the Sass::Prelexer::re_linebreak function in lexer.cpp in LibSass 3.4.5. A crafted input will lead to a remote denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1474276
