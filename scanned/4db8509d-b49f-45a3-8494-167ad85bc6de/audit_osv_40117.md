# [H] Net::CIDR::Set versions through 0.20 for Perl did not validate IP addresses

## Summary
Severity: High
Advisory: CVE-2026-49941
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-49941
Type: osv

## Details
Net::CIDR::Set versions through 0.20 for Perl did not validate IP addresses.

The add method called the _encode method to parse addresses. If the addresses did not look like netmasks or network ranges, then they were assumed to single IP addresses and passed back to itself as a 32-bit or 128-bit netmask.

If the argument was not a well-formed IP address, then this would lead to indefinite recursion.

An attacker could use this to cause a denial of service.

## References
- http://www.openwall.com/lists/oss-security/2026/06/04/11
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49941.json
- https://metacpan.org/release/RRWO/Net-CIDR-Set-0.21/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-49941
- https://github.com/robrwo/perl-Net-CIDR-Set
