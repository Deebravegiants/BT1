# [M] Improper Input Validation in Buildah and Podman

## Summary
Severity: Medium
Advisory: GHSA-fhqq-8f65-5xfc
CVE: CVE-2024-9407
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-10-01
Source: https://github.com/advisories/GHSA-fhqq-8f65-5xfc
Type: github-advisory

## Affected
- Go: `github.com/containers/buildah` — affected >=0 <1.37.4
- Go: `github.com/containers/podman/v5` — affected >=0 <5.2.4
- Go: `github.com/containers/podman` — affected >=0 <5.2.4
- Go: `github.com/containers/podman/v2` — affected >=0 <5.2.4
- Go: `github.com/containers/podman/v3` — affected >=0 <5.2.4
- Go: `github.com/containers/podman/v4` — affected >=0 <5.2.4

## Details
A vulnerability exists in the bind-propagation option of the Dockerfile RUN --mount instruction. The system does not properly validate the input passed to this option, allowing users to pass arbitrary parameters to the mount instruction. This issue can be exploited to mount sensitive directories from the host into a container during the build process and, in some cases, modify the contents of those mounted files. Even if SELinux is used, this vulnerability can bypass its protection by allowing the source directory to be relabeled to give the container access to host files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9407
- https://github.com/containers/buildah/commit/e4e2ad5ca2088d7c388109394135ead7aaf1f4f4
- https://access.redhat.com/errata/RHSA-2024:10147
- https://access.redhat.com/errata/RHSA-2024:8846
- https://access.redhat.com/errata/RHSA-2024:9051
- https://access.redhat.com/errata/RHSA-2024:9454
- https://access.redhat.com/errata/RHSA-2024:9459
- https://access.redhat.com/errata/RHSA-2024:9926
- https://access.redhat.com/security/cve/CVE-2024-9407
- https://bugzilla.redhat.com/show_bug.cgi?id=2315887
- https://github.com/containers/podman/releases/tag/v5.2.4
- https://pkg.go.dev/vuln/GO-2024-3169
- https://security.netapp.com/advisory/ntap-20241220-0010
