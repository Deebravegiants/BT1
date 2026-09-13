# [H] Podman Improper Certificate Validation; machine missing TLS verification

## Summary
Severity: High
Advisory: GHSA-65gg-3w2w-hr4h
CVE: CVE-2025-6032
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-25
Source: https://github.com/advisories/GHSA-65gg-3w2w-hr4h
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v4` — affected >=4.8.0
- Go: `github.com/containers/podman/v5` — affected >=0 <5.5.2

## Details
### Impact
The podman machine init command fails to verify the TLS certificate when downloading the VM images from an OCI registry (which it does by default since 5.0.0) allowing a possible Man In The Middle attack.

### Patches
https://github.com/containers/podman/commit/726b506acc8a00d99f1a3a1357ecf619a1f798c3
Fixed in v5.5.2

### Workarounds
Download the disk image manually via some other tool that verifies the TLS connection. Then pass the local image as file path (podman machine init --image ./somepath)

## References
- https://github.com/containers/podman/security/advisories/GHSA-65gg-3w2w-hr4h
- https://nvd.nist.gov/vuln/detail/CVE-2025-6032
- https://github.com/containers/podman/commit/726b506acc8a00d99f1a3a1357ecf619a1f798c3
- https://github.com/containers/podman
- https://bugzilla.redhat.com/show_bug.cgi?id=2372501
- https://access.redhat.com/security/cve/CVE-2025-6032
- https://access.redhat.com/errata/RHSA-2025:9766
- https://access.redhat.com/errata/RHSA-2025:9751
- https://access.redhat.com/errata/RHSA-2025:9726
- https://access.redhat.com/errata/RHSA-2025:15397
- https://access.redhat.com/errata/RHSA-2025:11681
- https://access.redhat.com/errata/RHSA-2025:11677
- https://access.redhat.com/errata/RHSA-2025:11363
- https://access.redhat.com/errata/RHSA-2025:11359
- https://access.redhat.com/errata/RHSA-2025:10668
- https://access.redhat.com/errata/RHSA-2025:10551
- https://access.redhat.com/errata/RHSA-2025:10550
- https://access.redhat.com/errata/RHSA-2025:10549
- https://access.redhat.com/errata/RHSA-2025:10295
