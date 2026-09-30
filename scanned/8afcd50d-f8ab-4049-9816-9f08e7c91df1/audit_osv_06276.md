# [H] NULL pointer dereference in SOAP apache:Map decoder with missing <value>

## Summary
Severity: High
Advisory: BIT-libphp-2026-7262
Aliases: BIT-php-2026-7262, BIT-php-min-2026-7262, CVE-2026-7262
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2026-7262
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.2.* before 8.2.31, 8.3.* before 8.3.31, 8.4.* before 8.4.21, and 8.5.* before 8.5.6, when a SOAP server has a typemap configured, the decoding process contains a mistake which checks the wrong variable in case of missing value element.  This leads to dereferences a NULL pointer, causing a segmentation fault. This allows a remote unauthenticated attacker to crash the PHP SOAP server process, resulting in denial of service.

## References
- https://github.com/php/php-src/security/advisories/GHSA-hmxp-6pc4-f3vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-7262
- https://access.redhat.com/errata/RHSA-2026:22142
- https://access.redhat.com/errata/RHSA-2026:22143
- https://access.redhat.com/errata/RHSA-2026:22305
- https://access.redhat.com/errata/RHSA-2026:22649
- https://access.redhat.com/errata/RHSA-2026:23388
- https://access.redhat.com/errata/RHSA-2026:33449
- https://access.redhat.com/errata/RHSA-2026:34354
- https://access.redhat.com/security/cve/CVE-2026-7262
- https://bugzilla.redhat.com/show_bug.cgi?id=2468565
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-7262.json
