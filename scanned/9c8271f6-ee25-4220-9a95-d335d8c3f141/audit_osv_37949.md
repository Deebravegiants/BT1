# [M] FreeRDP: Progressive Codec Quant BYTE Underflow - UB + CPU DoS

## Summary
Severity: Medium
Advisory: CVE-2026-33983
Aliases: GHSA-4gfm-4p52-h478
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33983
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, progressive_decompress_tile_upgrade() detects a mismatch via progressive_rfx_quant_cmp_equal() but only emits WLog_WARN, execution continues. The wrapped value (247) is used as a shift exponent, causing undefined behavior and an approximately 80 billion iteration loop (CPU DoS). This issue has been patched in version 3.24.2.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33983.json
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
- https://access.redhat.com/security/cve/CVE-2026-33983
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33983.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-4gfm-4p52-h478
- https://nvd.nist.gov/vuln/detail/CVE-2026-33983
- https://bugzilla.redhat.com/show_bug.cgi?id=2453220
