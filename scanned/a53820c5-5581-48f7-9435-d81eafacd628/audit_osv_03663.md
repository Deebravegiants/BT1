# [M] ALPINE-CVE-2026-40199

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-40199
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40199
Type: osv

## Affected
- Alpine:v3.21: `perl-net-cidr-lite` — affected >=0 <0.23-r0
- Alpine:v3.22: `perl-net-cidr-lite` — affected >=0 <0.23-r0
- Alpine:v3.23: `perl-net-cidr-lite` — affected >=0 <0.23-r0
- Alpine:v3.24: `perl-net-cidr-lite` — affected >=0 <0.23-r0

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
- https://security.alpinelinux.org/vuln/CVE-2026-40199
