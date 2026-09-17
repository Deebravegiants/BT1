# [H] Archive::Tar versions before 3.10 for Perl allow memory exhaustion via attacker controlled entry size field in tar header

## Summary
Severity: High
Advisory: CVE-2026-9538
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-9538
Type: osv

## Details
Archive::Tar versions before 3.10 for Perl allow memory exhaustion via attacker controlled entry size field in tar header.

_read_tar() reads each entry's payload with $handle->read($$data, $block), where $block is derived from the entry's 12-byte size field in the tar header with no upper bound on that value.

A crafted header declaring a multi-gigabyte size causes Perl to allocate a scalar of that size.

## References
- http://www.openwall.com/lists/oss-security/2026/05/26/4
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9538.json
- https://metacpan.org/release/BINGOS/Archive-Tar-3.10/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9538
- https://github.com/jib/archive-tar-new/commit/f9af01426038e29d9578825a0cd3626946ab08c7.patch
- https://github.com/jib/archive-tar-new
