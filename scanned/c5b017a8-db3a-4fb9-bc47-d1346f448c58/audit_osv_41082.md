# [C] Storable versions before 3.41 for Perl have a signed integer overflow when deserializing a crafted SX_HOOK record

## Summary
Severity: Critical
Advisory: CVE-2026-57433
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-57433
Type: osv

## Details
Storable versions before 3.41 for Perl have a signed integer overflow when deserializing a crafted SX_HOOK record.

retrieve_hook_common reads a signed 32-bit item count from an SX_HOOK record and calls av_extend with that count plus one. A count of I32_MAX wraps the addition to a negative value.

A crafted blob passed to thaw or retrieve triggers the overflow; av_extend receives the negative count and dies with a panic, terminating the deserialization.

## References
- http://www.openwall.com/lists/oss-security/2026/07/13/7
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57433.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57433
- https://github.com/Perl/perl5/commit/e4f681784bcdeaa91ff02a2fa4cdcae5c46779d7.patch
- https://github.com/Perl/perl5
