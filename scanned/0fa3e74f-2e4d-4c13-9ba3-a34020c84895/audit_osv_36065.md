# [H] Net::CIDR::Set versions before 0.23 for Perl allow memory exhaustion and malformed set ranges via unbounded IPv6 prefix lengths

## Summary
Severity: High
Advisory: CVE-2026-19566
Aliases: GHSA-grjr-r4x5-mx4p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19566
Type: osv

## Details
Net::CIDR::Set versions before 0.23 for Perl allow memory exhaustion and malformed set ranges via unbounded IPv6 prefix lengths.

The _encode method accepts any prefix length matching `(0|[1-9][0-9]*)` and passes it to _width2bits(), which builds the mask as `'1' x ($width + 8)`, one character per bit. The _inc() method then unpacks the packed mask into a Perl array of one scalar per byte, so the prefix length alone sets the allocation size: `::/100000000` builds a 100 MB string and a 12.5 million element array. The value being tested is parsed, not just the configured ranges: contains() builds a set from its argument, and _guess_coder() tries the IPv4 coder and then the IPv6 coder, so an IPv4-only set expands an oversized IPv6 prefix length before the mixed address width check rejects it.

Any caller that passes untrusted input to contains() or add() can exhaust process memory. A prefix length above 128 is also stored as a range that does not match the requested block: 2001:db8::/129 stringifies back unchanged, contains() of its own base address returns false, and removing it from a set drops the base address while the set still prints as covering it.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-49942
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19566.json
- https://github.com/robrwo/perl-Net-CIDR-Set/security/advisories/GHSA-grjr-r4x5-mx4p
- https://metacpan.org/release/RRWO/Net-CIDR-Set-0.23/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-19566
- https://github.com/robrwo/perl-Net-CIDR-Set/commit/e16b27db676fd1ca671fbb31208a22c1b1ba9724.patch
- https://github.com/robrwo/perl-Net-CIDR-Set
