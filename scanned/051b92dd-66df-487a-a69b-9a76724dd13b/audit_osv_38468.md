# [M] Net::CIDR::Lite versions before 0.23 for Perl mishandles IPv4 mapped IPv6 addresses, which may allow IP ACL bypass

## Summary
Severity: Medium
Advisory: CVE-2026-40199
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40199
Type: osv

## Details
Net::CIDR::Lite versions before 0.23 for Perl mishandles IPv4 mapped IPv6 addresses, which may allow IP ACL bypass.

_pack_ipv6() includes the sentinel byte from _pack_ipv4() when building the packed representation of IPv4 mapped addresses like ::ffff:192.168.1.1. This produces an 18 byte value instead of 17 bytes, misaligning the IPv4 part of the address.

The wrong length causes incorrect results in mask operations (bitwise AND truncates to the shorter operand) and in find() / bin_find() which use Perl string comparison (lt/gt). This can cause find() to incorrectly match or miss addresses.

Example:

  my $cidr = Net::CIDR::Lite->new("::ffff:192.168.1.0/120");
  $cidr->find("::ffff:192.168.2.0");  # incorrectly returns true

This is triggered by valid RFC 4291 IPv4 mapped addresses (::ffff:x.x.x.x).

See also CVE-2026-40198, a related issue in the same function affecting malformed IPv6 addresses.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-40198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40199.json
- https://metacpan.org/release/STIGTSP/Net-CIDR-Lite-0.23/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-40199
- https://github.com/stigtsp/Net-CIDR-Lite/commit/b7166b1fa17b3b14b4c795ace5b3fbf71a0bd04a.patch
- https://github.com/stigtsp/Net-CIDR-Lite
