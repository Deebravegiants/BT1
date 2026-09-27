# [H] Libxml2: integer overflow in xmlbuildqname() leads to stack buffer overflow in libxml2

## Summary
Severity: High
Advisory: BIT-java-2025-6021
Aliases: BIT-java-min-2025-6021, BIT-jre-2025-6021, CVE-2025-6021
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-6021
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.481

## Details
A flaw was found in libxml2's xmlBuildQName function, where integer overflows in buffer size calculations can lead to a stack-based buffer overflow. This issue can result in memory corruption or a denial of service when processing crafted input.

## References
- https://access.redhat.com/errata/RHSA-2025:10630
- https://access.redhat.com/errata/RHSA-2025:10698
- https://access.redhat.com/errata/RHSA-2025:10699
- https://access.redhat.com/errata/RHSA-2025:11580
- https://access.redhat.com/errata/RHSA-2025:11673
- https://access.redhat.com/errata/RHSA-2025:12098
- https://access.redhat.com/errata/RHSA-2025:12099
- https://access.redhat.com/errata/RHSA-2025:12199
- https://access.redhat.com/errata/RHSA-2025:12237
- https://access.redhat.com/errata/RHSA-2025:12239
- https://access.redhat.com/errata/RHSA-2025:12240
- https://access.redhat.com/errata/RHSA-2025:12241
- https://access.redhat.com/errata/RHSA-2025:13267
- https://access.redhat.com/errata/RHSA-2025:13289
- https://access.redhat.com/errata/RHSA-2025:13325
- https://access.redhat.com/errata/RHSA-2025:13335
- https://access.redhat.com/errata/RHSA-2025:13336
- https://access.redhat.com/errata/RHSA-2025:14059
- https://access.redhat.com/errata/RHSA-2025:14396
- https://access.redhat.com/errata/RHSA-2025:15308
