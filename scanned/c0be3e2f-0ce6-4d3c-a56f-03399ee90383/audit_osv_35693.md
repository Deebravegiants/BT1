# [H] List::SomeUtils::XS versions before 0.59 for Perl have a heap buffer overflow in the pairwise function

## Summary
Severity: High
Advisory: CVE-2026-12844
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-12844
Type: osv

## Details
List::SomeUtils::XS versions before 0.59 for Perl have a heap buffer overflow in the pairwise function.

pairwise() collects the values returned by the block into a heap buffer sized to the longer input array, then grows the buffer before each copy with a single quadrupling (alloc <<= 2) instead of a loop. A block call that returns more than four times the current allocation in one invocation outgrows that one quadrupling, and the copy writes past the end of the buffer.

Any caller of pairwise() whose block returns, for a single pair, more than four times the longer input array's length writes past the buffer and corrupts the heap.

## References
- http://www.openwall.com/lists/oss-security/2026/06/25/11
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12844.json
- https://metacpan.org/release/DROLSKY/List-SomeUtils-XS-0.59/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-12844
- https://github.com/houseabsolute/List-SomeUtils-XS/commit/22549f78669b780d6aa338a2d2e49a3dedfffaa6.patch
- https://github.com/houseabsolute/List-SomeUtils-XS
