# [M] Perl versions through 5.45.1 have out-of-bounds heap reads and writes during regular expression matching via an undersized superlinear cache in S_regmatch

## Summary
Severity: Medium
Advisory: CVE-2026-15534
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/CVE-2026-15534
Type: osv

## Details
Perl versions through 5.45.1 have out-of-bounds heap reads and writes during regular expression matching via an undersized superlinear cache in S_regmatch.

The regex engine's superlinear cache holds one bit per subject position for each participating WHILEM node, so the bit count is the subject length plus one times the number of nodes. Nothing checks that product for positive overflow of the signed 32-bit count: a 286331153 byte subject matched against a pattern with 15 participating nodes stores the count as 14, leaving a two byte cache. The cache is then indexed from the real match position and node number, so reads go past the end of the allocation, and on failure CACHEsayNO sets a bit past it.

A caller that matches an attacker controlled subject of this size against a pattern of this shape can crash the process or corrupt heap memory.

## References
- http://www.openwall.com/lists/oss-security/2026/08/09/12
- http://www.openwall.com/lists/oss-security/2026/08/09/13
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15534.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15534
- https://github.com/Perl/perl5/commit/54cf3d44cbbedd17d774e9a37921963e8fd5d0cb.patch
- https://github.com/Perl/perl5/commit/568e6fd238867bb9e99fa3f47cba3169009239e0.patch
- https://github.com/Perl/perl5
