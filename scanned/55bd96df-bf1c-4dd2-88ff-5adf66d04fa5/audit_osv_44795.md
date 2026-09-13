# [H] Net::IP::LPM versions before 1.12 for Perl accept malformed prefix lengths

## Summary
Severity: High
Advisory: CVE-2026-86287
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86287
Type: osv

## Details
Net::IP::LPM versions before 1.12 for Perl accept malformed prefix lengths.

Non-numeric and non-ASCII prefix lengths are accepted and treated as 0. Integers over 31 bits are silently truncated.  A single malformed mask will poison the lookup table.

The result is that the lookup will silently succeed for every address. An allow-list will allow every address, and a deny-list will block every address.

## References
- http://www.openwall.com/lists/oss-security/2026/09/07/1
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86287.json
- https://metacpan.org/release/RRWO/Net-IP-LPM-1.12/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-86287
- https://github.com/robrwo/perl-Net-IP-LPM/commit/814f8baa85537827db8c3b3d251e48db7aca318f.patch
- https://github.com/robrwo/perl-Net-IP-LPM
