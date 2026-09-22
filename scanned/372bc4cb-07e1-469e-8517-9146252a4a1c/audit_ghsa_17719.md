# [H] Buildah allows build breakout using malicious Containerfiles and concurrent builds

## Summary
Severity: High
Advisory: GHSA-5vpc-35f4-r8w6
CVE: CVE-2024-11218
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-5vpc-35f4-r8w6
Type: github-advisory

## Affected
- Go: `github.com/containers/buildah` — affected >=1.38.0 <1.38.1
- Go: `github.com/containers/buildah` — affected >=1.37.0 <1.37.6
- Go: `github.com/containers/buildah` — affected >=1.35.0 <1.35.5
- Go: `github.com/containers/buildah` — affected >=0 <1.33.12

## Details
### Impact
With careful use of the `--mount` flag in RUN instructions in Containerfiles, and by using either multi-stage builds with use of concurrently-executing build stages (e.g., using the `--jobs` CLI flag) or multiple separate but concurrently-executing builds, a malicious Containerfile can be used to expose content from the build host to the command being run using the RUN instruction.  This can be used to read or write contents using the privileges of the process which is performing the build.  When that process is a root-owned podman system service which is provided for use by unprivileged users, this includes the ability to read and write contents which the client should not be allowed to read and write, including setuid executables in locations where they can be later accessed by unprivileged users.

### Patches
Patches have been merged to the main branch, and will be added to upcoming releases on the release-1.38, release-1.37, release-1.35, and release-1.33 branches.

This addressed a number of Jira cards, but primarily https://issues.redhat.com/browse/RHEL-67616 and https://issues.redhat.com/browse/RHEL-67618, which were then vendored into Podman and backported into olde rbranches.

### Workarounds
Mandatory access controls should limit the access of the process performing the build, on systems where they are enabled.

## References
- https://github.com/containers/buildah/security/advisories/GHSA-5vpc-35f4-r8w6
- https://nvd.nist.gov/vuln/detail/CVE-2024-11218
- https://github.com/containers/buildah/pull/5918
- https://access.redhat.com/errata/RHSA-2025:0830
- https://access.redhat.com/errata/RHSA-2025:2441
- https://access.redhat.com/errata/RHSA-2025:2443
- https://access.redhat.com/errata/RHSA-2025:2454
- https://access.redhat.com/errata/RHSA-2025:2456
- https://access.redhat.com/errata/RHSA-2025:2701
- https://access.redhat.com/errata/RHSA-2025:2703
- https://access.redhat.com/errata/RHSA-2025:2710
- https://access.redhat.com/errata/RHSA-2025:2712
- https://access.redhat.com/errata/RHSA-2025:3577
- https://access.redhat.com/errata/RHSA-2025:3798
- https://access.redhat.com/security/cve/CVE-2024-11218
- https://bugzilla.redhat.com/show_bug.cgi?id=2326231
- https://github.com/containers/buildah
- https://issues.redhat.com/browse/RHEL-67616
- https://issues.redhat.com/browse/RHEL-67618
- https://access.redhat.com/errata/RHSA-2025:0878
