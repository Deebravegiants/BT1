# [M] Perl versions from 5.9.4 before 5.41.9 produce incorrect regular expression match results when a stale failure flag ends the Aho-Corasick prescan early in S_find_byclass

## Summary
Severity: Medium
Advisory: CVE-2026-19487
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-19487
Type: osv

## Details
Perl versions from 5.9.4 before 5.41.9 produce incorrect regular expression match results when a stale failure flag ends the Aho-Corasick prescan early in S_find_byclass.

The prescan walks the subject for positions where the full pattern could match, and the engine tries it from the leftmost one recorded. A failing transition sets the failed flag, and a later successful transition does not clear it, so the prescan reads the stale flag as a failure and stops before it can record a candidate that starts earlier. It takes a subject where one candidate is recorded and a later character then forces a fallback through a fail link that succeeds.

Example:

  "ABCDE" =~ m/ABCF|BCDE|C/;    # matches C at offset 2, not BCDE
  "ABCDE" =~ m/ABCF|BCDE|C(G)/; # no match, BCDE missed

An alternation like this can miss input it should match, or match it on the wrong branch, so an access or filtering decision made from the result can be wrong.

## References
- http://www.openwall.com/lists/oss-security/2026/08/13/8
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19487.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19487
- https://github.com/Perl/perl5/issues/22892
- https://github.com/Perl/perl5/commit/1a21abacaf6f684928bae8baaa153733c8c238eb.patch
- https://github.com/Perl/perl5
