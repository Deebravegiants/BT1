# [C] Perl versions before 5.40.5-RC1, from 5.41.0 before 5.42.3-RC1, from 5.43.0 before 5.43.10 produce silently incorrect regular expression matches when an alternation of more than 65535 fixed string branches is compiled into a trie in Perl_study_chunk

## Summary
Severity: Critical
Advisory: CVE-2026-13221
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-13221
Type: osv

## Details
Perl versions before 5.40.5-RC1, from 5.41.0 before 5.42.3-RC1, from 5.43.0 before 5.43.10 produce silently incorrect regular expression matches when an alternation of more than 65535 fixed string branches is compiled into a trie in Perl_study_chunk.

When such branches are combined into a trie, the delta between the first branch and the shared tail is stored in a 16-bit field. A branch count above 65535 overflows the field, and the trie's match decision table is truncated with no warning or error.

A pattern of this shape produces false positive matches (matching strings it should not) and false negative matches (failing to match strings it should). When such a pattern gates an access or filtering decision, the result is wrong.

## References
- http://www.openwall.com/lists/oss-security/2026/07/13/5
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13221.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13221
- https://github.com/Perl/perl5/issues/23388
- https://github.com/Perl/perl5/commit/03f74bbbd3a68350d926ee93d56ee4808c28c4c7.patch
- https://github.com/Perl/perl5
