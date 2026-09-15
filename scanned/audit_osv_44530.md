# [H] Perl versions before 5.40.5-RC1, from 5.41.0 before 5.42.3-RC1, from 5.43.0 before 5.43.11 have a heap buffer overflow when compiling regular expressions with a repeated fixed string on 32-bit builds

## Summary
Severity: High
Advisory: CVE-2026-8376
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/CVE-2026-8376
Type: osv

## Details
Perl versions before 5.40.5-RC1, from 5.41.0 before 5.42.3-RC1, from 5.43.0 before 5.43.11 have a heap buffer overflow when compiling regular expressions with a repeated fixed string on 32-bit builds.

Perl_study_chunk in regcomp_study.c checked the size of the joined substring buffer in characters rather than bytes. For a quantified fixed substring with a large minimum count, the byte length mincount * l could overflow SSize_t, producing an undersized SvGROW allocation; the subsequent copy writes past the end of the buffer.

A caller that compiles an attacker-controlled regular expression on a 32-bit perl build triggers a heap buffer overflow at compile time.

## References
- http://www.openwall.com/lists/oss-security/2026/05/26/1
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8376.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8376
- https://github.com/Perl/perl5/commit/5e7f119eb2bb1181be908701f22bf7068e722f1c.patch
- https://github.com/Perl/perl5
