# [C] Use-After-Free in SOAP using Apache map

## Summary
Severity: Critical
Advisory: BIT-libphp-2026-6722
Aliases: BIT-php-2026-6722, BIT-php-min-2026-6722, CVE-2026-6722
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2026-6722
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.2.* before 8.2.31, 8.3.* before 8.3.31, 8.4.* before 8.4.21, and 8.5.* before 8.5.6, the SOAP extension's object deduplication mechanism stores pointers to PHP objects in a global map without incrementing their reference counts. When an apache:Map node contains duplicate keys, processing the second entry overwrites the first in the temporary result map, freeing the original PHP object while its stale pointer remains in the map. A subsequent href reference to the freed node can copy the dangling pointer into the result. As PHP string allocations can reclaim the freed memory region, an attacker with control over the SOAP request body can exploit this use-after-free to achieve remote code execution.

## References
- https://github.com/php/php-src/security/advisories/GHSA-85c2-q967-79q5
- https://nvd.nist.gov/vuln/detail/CVE-2026-6722
- https://access.redhat.com/errata/RHSA-2026:33449
- https://access.redhat.com/errata/RHSA-2026:34354
- https://access.redhat.com/security/cve/CVE-2026-6722
- https://bugzilla.redhat.com/show_bug.cgi?id=2468560
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-6722.json
- https://access.redhat.com/errata/RHSA-2026:22142
- https://access.redhat.com/errata/RHSA-2026:22143
- https://access.redhat.com/errata/RHSA-2026:22305
- https://access.redhat.com/errata/RHSA-2026:22649
- https://access.redhat.com/errata/RHSA-2026:23388
