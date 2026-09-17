# [H] A vulnerability has been identified in the libarchive library, specifically within the...

## Summary
Severity: High
Advisory: JLSEC-2025-245
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-245
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.8.0+0

## Details
A vulnerability has been identified in the libarchive library, specifically within the `archive_read_format_rar_seek_data()` function. This flaw involves an integer overflow that can ultimately lead to a double-free condition. Exploiting a double-free vulnerability can result in memory corruption, enabling an attacker to execute arbitrary code or cause a denial-of-service condition.

## References
- https://access.redhat.com/errata/RHSA-2025:14130
- https://access.redhat.com/errata/RHSA-2025:14135
- https://access.redhat.com/errata/RHSA-2025:14137
- https://access.redhat.com/errata/RHSA-2025:14141
- https://access.redhat.com/errata/RHSA-2025:14142
- https://access.redhat.com/errata/RHSA-2025:14525
- https://access.redhat.com/errata/RHSA-2025:14528
- https://access.redhat.com/errata/RHSA-2025:14594
- https://access.redhat.com/errata/RHSA-2025:14644
- https://access.redhat.com/errata/RHSA-2025:14808
- https://access.redhat.com/errata/RHSA-2025:14810
- https://access.redhat.com/errata/RHSA-2025:14828
- https://access.redhat.com/errata/RHSA-2025:15024
- https://access.redhat.com/errata/RHSA-2025:15397
- https://access.redhat.com/errata/RHSA-2025:15709
- https://access.redhat.com/errata/RHSA-2025:15827
- https://access.redhat.com/errata/RHSA-2025:15828
- https://access.redhat.com/errata/RHSA-2025:16524
- https://access.redhat.com/errata/RHSA-2025:18217
- https://access.redhat.com/errata/RHSA-2025:18218
