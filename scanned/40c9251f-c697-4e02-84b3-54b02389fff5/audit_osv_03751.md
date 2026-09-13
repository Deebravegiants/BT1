# [M] ALPINE-CVE-2026-45190

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-45190
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-45190
Type: osv

## Affected
- Alpine:v3.24: `perl-net-cidr-lite` — affected >=0 <0.24-r0

## Details
Net::CIDR::Lite versions before 0.24 for Perl does not properly validate IP address and CIDR mask inputs, which may allow IP ACL bypass.

Inputs containing a trailing newline or non-ASCII digit characters pass the validators but are then re-encoded by the parser to a different address than the input string spelled. find() and bin_find() can match or miss addresses as a result.

Example:

  my $cidr = Net::CIDR::Lite->new();
  $cidr->add("::1\n/128");
  $cidr->find("::1a");  # incorrectly returns true

See also CVE-2026-45191.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-45190
