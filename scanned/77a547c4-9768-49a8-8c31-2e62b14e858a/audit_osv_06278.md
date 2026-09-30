# [H] Signed integer overflow in metaphone()

## Summary
Severity: High
Advisory: BIT-libphp-2026-7568
Aliases: BIT-php-2026-7568, BIT-php-min-2026-7568, CVE-2026-7568
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2026-7568
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.2.* before 8.2.31, 8.3.* before 8.3.31, 8.4.* before 8.4.21, and 8.5.* before 8.5.6, the metaphone() function in ext/standard/metaphone.c uses a signed int variable to track the current position within the input string. If a string longer than 2,147,483,647 bytes is passed, a signed integer overflow occurs, resulting in undefined behavior. This can lead to an out-of-bounds read, causing a segmentation fault or access to unrelated memory, and may affect the availability of the PHP process.

## References
- https://github.com/php/php-src/security/advisories/GHSA-96wq-48vp-hh57
- https://nvd.nist.gov/vuln/detail/CVE-2026-7568
- https://access.redhat.com/errata/RHSA-2026:22142
- https://access.redhat.com/errata/RHSA-2026:22143
- https://access.redhat.com/errata/RHSA-2026:22305
- https://access.redhat.com/errata/RHSA-2026:22649
- https://access.redhat.com/errata/RHSA-2026:23388
- https://access.redhat.com/errata/RHSA-2026:33449
- https://access.redhat.com/errata/RHSA-2026:34354
- https://access.redhat.com/security/cve/CVE-2026-7568
- https://bugzilla.redhat.com/show_bug.cgi?id=2468566
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-7568.json
