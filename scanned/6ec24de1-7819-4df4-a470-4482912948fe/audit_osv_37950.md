# [H] FreeRDP: ClearCodec resize_vbar_entry() Heap OOB Write

## Summary
Severity: High
Advisory: CVE-2026-33984
Aliases: GHSA-8469-2xcx-frf6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33984
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, in resize_vbar_entry() in libfreerdp/codec/clear.c, vBarEntry->size is updated to vBarEntry->count before the winpr_aligned_recalloc() call. If realloc fails, size is inflated while pixels still points to the old, smaller buffer. On a subsequent call where count <= size (the inflated value), realloc is skipped. The caller then writes count * bpp bytes of attacker-controlled pixel data into the undersized buffer, causing a heap buffer overflow. This issue has been patched in version 3.24.2.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33984.json
- https://access.redhat.com/errata/RHSA-2026:10709
- https://access.redhat.com/errata/RHSA-2026:11332
- https://access.redhat.com/errata/RHSA-2026:11333
- https://access.redhat.com/errata/RHSA-2026:11336
- https://access.redhat.com/errata/RHSA-2026:11649
- https://access.redhat.com/errata/RHSA-2026:11651
- https://access.redhat.com/errata/RHSA-2026:12359
- https://access.redhat.com/errata/RHSA-2026:12388
- https://access.redhat.com/errata/RHSA-2026:19033
- https://access.redhat.com/errata/RHSA-2026:19349
- https://access.redhat.com/errata/RHSA-2026:8457
- https://access.redhat.com/errata/RHSA-2026:8458
- https://access.redhat.com/errata/RHSA-2026:8945
- https://access.redhat.com/errata/RHSA-2026:9656
- https://access.redhat.com/security/cve/CVE-2026-33984
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33984.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-8469-2xcx-frf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33984
- https://bugzilla.redhat.com/show_bug.cgi?id=2453219
