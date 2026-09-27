# [H] A flaw was found in libxml2's xmlBuildQName function, where integer overflows in buffer size...

## Summary
Severity: High
Advisory: JLSEC-2025-196
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/JLSEC-2025-196
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.14.4+0

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
