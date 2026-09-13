# [M] Net::Dropbear versions through 0.16 for Perl contains a dependency that may be susceptible to an integer overflow

## Summary
Severity: Medium
Advisory: CVE-2025-40913
Aliases: CVE-2025-40914, GHSA-j3xv-6967-cv88
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/CVE-2025-40913
Type: osv

## Details
Net::Dropbear versions through 0.16 for Perl contains a dependency that may be susceptible to an integer overflow.

Net::Dropbear embeds a version of the libtommath library that is susceptible to an integer overflow associated with CVE-2023-36328.

## References
- https://cpan.org/modules
- https://metacpan.org/release/ATRODO/Net-Dropbear-0.16/source/dropbear/libtommath/bn_mp_grow.c
- https://www.cve.org/CVERecord?id=CVE-2023-36328
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40913.json
- https://github.com/advisories/GHSA-j3xv-6967-cv88
- https://nvd.nist.gov/vuln/detail/CVE-2025-40913
- https://github.com/libtom/libtommath/pull/546
- https://github.com/atrodo/Net-Dropbear
