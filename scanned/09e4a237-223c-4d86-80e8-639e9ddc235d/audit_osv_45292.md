# [H] A flaw was found in rsync which could be triggered when rsync compares file checksums

## Summary
Severity: High
Advisory: JLSEC-2025-324
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-324
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.3.0+0

## Details
A flaw was found in rsync which could be triggered when rsync compares file checksums. This flaw allows an attacker to manipulate the checksum length (s2length) to cause a comparison between a checksum and uninitialized memory and leak one byte of uninitialized stack data at a time.

## References
- https://access.redhat.com/errata/RHBA-2025:6470
- https://access.redhat.com/errata/RHSA-2025:0324
- https://access.redhat.com/errata/RHSA-2025:0325
- https://access.redhat.com/errata/RHSA-2025:0637
- https://access.redhat.com/errata/RHSA-2025:0688
- https://access.redhat.com/errata/RHSA-2025:0714
- https://access.redhat.com/errata/RHSA-2025:0774
- https://access.redhat.com/errata/RHSA-2025:0787
- https://access.redhat.com/errata/RHSA-2025:0790
- https://access.redhat.com/errata/RHSA-2025:0849
- https://access.redhat.com/errata/RHSA-2025:0884
- https://access.redhat.com/errata/RHSA-2025:0885
- https://access.redhat.com/errata/RHSA-2025:1120
- https://access.redhat.com/errata/RHSA-2025:1123
- https://access.redhat.com/errata/RHSA-2025:1128
- https://access.redhat.com/errata/RHSA-2025:1225
- https://access.redhat.com/errata/RHSA-2025:1227
- https://access.redhat.com/errata/RHSA-2025:1242
- https://access.redhat.com/errata/RHSA-2025:1451
- https://access.redhat.com/errata/RHSA-2025:21885
