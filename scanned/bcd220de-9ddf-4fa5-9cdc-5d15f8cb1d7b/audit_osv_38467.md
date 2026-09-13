# [H] Net::CIDR::Lite versions before 0.23 for Perl does not validate IPv6 group count, which may allow IP ACL bypass

## Summary
Severity: High
Advisory: CVE-2026-40198
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40198
Type: osv

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
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-40199
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40198.json
- https://metacpan.org/release/STIGTSP/Net-CIDR-Lite-0.23/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-40198
- https://github.com/stigtsp/Net-CIDR-Lite/commit/25d65f85dbe4885959a10471725ec9d250a589c3.patch
- https://github.com/stigtsp/Net-CIDR-Lite
