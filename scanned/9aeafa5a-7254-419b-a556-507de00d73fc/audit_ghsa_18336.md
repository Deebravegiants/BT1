# [H] Podman Creates Temporary File with Insecure Permissions

## Summary
Severity: High
Advisory: GHSA-m68q-4hqr-mc6f
CVE: CVE-2025-4953
CWE: CWE-378
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-m68q-4hqr-mc6f
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v5` — affected >=0

## Details
A flaw was found in Podman. In a Containerfile or Podman, data written to RUN --mount=type=bind mounts during the podman build is not discarded. This issue can lead to files created within the container appearing in the temporary build context directory on the host, leaving the created files accessible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4953
- https://github.com/containers/podman/pull/25173
- https://github.com/containers/podman
- https://bugzilla.redhat.com/show_bug.cgi?id=2367235
- https://access.redhat.com/security/cve/CVE-2025-4953
- https://access.redhat.com/errata/RHSA-2026:0316
- https://access.redhat.com/errata/RHSA-2025:2703
- https://access.redhat.com/errata/RHSA-2025:23113
- https://access.redhat.com/errata/RHSA-2025:22732
- https://access.redhat.com/errata/RHSA-2025:22724
- https://access.redhat.com/errata/RHSA-2025:22695
- https://access.redhat.com/errata/RHSA-2025:22275
- https://access.redhat.com/errata/RHSA-2025:22265
- https://access.redhat.com/errata/RHSA-2025:17669
- https://access.redhat.com/errata/RHSA-2025:16729
- https://access.redhat.com/errata/RHSA-2025:16724
- https://access.redhat.com/errata/RHSA-2025:15904
- https://access.redhat.com/errata/RHSA-2024:8690
