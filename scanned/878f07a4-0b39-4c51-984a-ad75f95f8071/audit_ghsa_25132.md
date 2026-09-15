# [M] Podman Symlink Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r34v-gqmw-qvgj
CVE: CVE-2019-18466
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r34v-gqmw-qvgj
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v4` — affected >=0 <1.6.0

## Details
An issue was discovered in Podman in libpod before 1.6.0. It resolves a symlink in the host context during a copy operation from the container to the host, because an undesired glob operation occurs. An attacker could create a container image containing particular symlinks that, when copied by a victim user to the host filesystem, may overwrite existing files with others from the host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18466
- https://github.com/containers/libpod/issues/3829
- https://github.com/containers/libpod/commit/5c09c4d2947a759724f9d5aef6bac04317e03f7e
- https://access.redhat.com/errata/RHSA-2019:4269
- https://bugzilla.redhat.com/show_bug.cgi?id=1744588
- https://github.com/containers/libpod
- https://github.com/containers/libpod/compare/v1.5.1...v1.6.0
