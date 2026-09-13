# [C] Socket versions before 2.041 for Perl have an out-of-bounds heap read

## Summary
Severity: Critical
Advisory: CVE-2026-12087
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2026-12087
Type: osv

## Details
Socket versions before 2.041 for Perl have an out-of-bounds heap read.

In Socket.xs, pack_ip_mreq_source() checks the length of its source argument before the argument is read, so the check tests the byte length carried over from the preceding multiaddr argument instead. Both addresses occupy a 4-byte field, so a valid multiaddr lets a source of any length pass the check, and the source is then copied into the 4-byte imr_sourceaddr field with a fixed-size copy. A source shorter than 4 bytes is not rejected, and the copy reads up to 3 bytes past the end of its buffer.

Calling pack_ip_mreq_source() with a source value shorter than 4 bytes copies adjacent heap memory into the returned packed structure.

## References
- http://www.openwall.com/lists/oss-security/2026/06/15/10
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12087.json
- https://metacpan.org/release/PEVANS/Socket-2.041/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-12087
- https://github.com/Perl/perl5/commit/de19a0b0ad1900fef976c5c1400bd8f11ec6c6cb.patch
