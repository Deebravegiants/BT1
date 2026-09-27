# [C] CVE-2017-8399

## Summary
Severity: Critical
Advisory: CVE-2017-8399
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8399
Type: osv

## Details
PCRE2 before 10.30 has an out-of-bounds write caused by a stack-based buffer overflow in pcre2_match.c, related to a "pattern with very many captures."

## References
- https://vcs.pcre.org/pcre2/code/tags/pcre2-10.30/ChangeLog?revision=854&view=markup
- http://www.securityfocus.com/bid/98315
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=783
- https://security.gentoo.org/glsa/201710-09
- https://vcs.pcre.org/pcre2?view=revision&revision=674
