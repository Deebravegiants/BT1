# [H] ALPINE-CVE-2026-40198

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-40198
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40198
Type: osv

## Affected
- Alpine:v3.21: `perl-net-cidr-lite` — affected >=0 <0.23-r0
- Alpine:v3.22: `perl-net-cidr-lite` — affected >=0 <0.23-r0
- Alpine:v3.23: `perl-net-cidr-lite` — affected >=0 <0.23-r0
- Alpine:v3.24: `perl-net-cidr-lite` — affected >=0 <0.23-r0

## Details
Net::CIDR::Lite versions before 0.23 for Perl does not validate IPv6 group count, which may allow IP ACL bypass.

_pack_ipv6() does not check that uncompressed IPv6 addresses (without ::) have exactly 8 hex groups. Inputs like "abcd", "1:2:3", or "1:2:3:4:5:6:7" are accepted and produce packed values of wrong length (3, 7, or 15 bytes instead of 17).

The packed values are used internally for mask and comparison operations. find() and bin_find() use Perl string comparison (lt/gt) on these values, and comparing strings of different lengths gives wrong results. This can cause find() to incorrectly report an address as inside or outside a range.

Example:

  my $cidr = Net::CIDR::Lite->new("::/8");
  $cidr->find("1:2:3");  # invalid input, incorrectly returns true

This is the same class of input validation issue as CVE-2021-47154 (IPv4 leading zeros) previously fixed in this module.

See also CVE-2026-40199, a related issue in the same function affecting IPv4 mapped IPv6 addresses.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40198
