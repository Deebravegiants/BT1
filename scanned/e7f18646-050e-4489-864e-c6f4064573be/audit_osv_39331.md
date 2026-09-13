# [M] Net::CIDR::Lite versions before 0.24 for Perl does not properly validate IP address and CIDR mask inputs, which may allow IP ACL bypass

## Summary
Severity: Medium
Advisory: CVE-2026-45190
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-10
Source: https://osv.dev/vulnerability/CVE-2026-45190
Type: osv

## Details
Net::CIDR::Lite versions before 0.24 for Perl does not properly validate IP address and CIDR mask inputs, which may allow IP ACL bypass.

Inputs containing a trailing newline or non-ASCII digit characters pass the validators but are then re-encoded by the parser to a different address than the input string spelled. find() and bin_find() can match or miss addresses as a result.

Example:

  my $cidr = Net::CIDR::Lite->new();
  $cidr->add("::1\n/128");
  $cidr->find("::1a");  # incorrectly returns true

See also CVE-2026-45191.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-45191
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45190.json
- https://metacpan.org/release/STIGTSP/Net-CIDR-Lite-0.24/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-45190
- https://github.com/stigtsp/Net-CIDR-Lite/commit/ca9542adec87110556601d7ce48381ea8d13e692.patch
- https://github.com/stigtsp/Net-CIDR-Lite
