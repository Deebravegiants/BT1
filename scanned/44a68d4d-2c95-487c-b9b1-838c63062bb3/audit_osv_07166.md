# [C] BIT-node-2025-55130

## Summary
Severity: Critical
Advisory: BIT-node-2025-55130
Aliases: BIT-node-min-2025-55130, CVE-2025-55130
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-node-2025-55130
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.3.0

## Details
A flaw in Node.js’s Permissions model allows attackers to bypass `--allow-fs-read` and `--allow-fs-write` restrictions using crafted relative symlink paths. By chaining directories and symlinks, a script granted access only to the current directory can escape the allowed path and read sensitive files. This breaks the expected isolation guarantees and enables arbitrary file read/write, leading to potential system compromise.
This vulnerability affects users of the permission model on Node.js v20,  v22,  v24, and v25.

## References
- https://nodejs.org/en/blog/vulnerability/december-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-55130
- https://access.redhat.com/errata/RHSA-2026:1842
- https://access.redhat.com/errata/RHSA-2026:1843
- https://access.redhat.com/errata/RHSA-2026:2420
- https://access.redhat.com/errata/RHSA-2026:2421
- https://access.redhat.com/errata/RHSA-2026:2422
- https://access.redhat.com/errata/RHSA-2026:2767
- https://access.redhat.com/errata/RHSA-2026:2768
- https://access.redhat.com/errata/RHSA-2026:2781
- https://access.redhat.com/errata/RHSA-2026:2782
- https://access.redhat.com/errata/RHSA-2026:2783
- https://access.redhat.com/errata/RHSA-2026:2864
- https://access.redhat.com/errata/RHSA-2026:2899
- https://access.redhat.com/errata/RHSA-2026:6402
- https://access.redhat.com/errata/RHSA-2026:6431
- https://access.redhat.com/errata/RHSA-2026:7386
- https://access.redhat.com/errata/RHSA-2026:7387
- https://access.redhat.com/security/cve/CVE-2025-55130
- https://bugzilla.redhat.com/show_bug.cgi?id=2431352
