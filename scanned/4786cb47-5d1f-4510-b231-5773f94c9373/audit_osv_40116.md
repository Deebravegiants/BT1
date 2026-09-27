# [M] Net::CIDR::Set versions through 0.20 for Perl accept non-ASCII IP addresses and netmasks

## Summary
Severity: Medium
Advisory: CVE-2026-49940
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-49940
Type: osv

## Details
Net::CIDR::Set versions through 0.20 for Perl accept non-ASCII IP addresses and netmasks.

Unicode digits such as the Arabic-Indic One (U+0661) were accepted but not properly parsed as numbers.  This could allow network masks to accept larger networks.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49940.json
- https://metacpan.org/release/RRWO/Net-CIDR-Set-0.21/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-40911
- https://nvd.nist.gov/vuln/detail/CVE-2026-49940
- https://github.com/robrwo/perl-Net-CIDR-Set
