# [M] Podman has Files or Directories Accessible to External Parties

## Summary
Severity: Medium
Advisory: GHSA-vmhj-p9hw-vgrf
CVE: CVE-2020-1726
CWE: CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vmhj-p9hw-vgrf
Type: github-advisory

## Affected
- Go: `github.com/containers/podman` — affected >=1.6.0 <2.0.6
- Go: `github.com/containers/podman/v2` — affected >=0 <2.0.6

## Details
A flaw was discovered in Podman where it incorrectly allows containers when created to overwrite existing files in volumes, even if they are mounted as read-only. When a user runs a malicious container or a container based on a malicious image with an attached volume that is used for the first time, it is possible to trigger the flaw and overwrite files in the volume. This issue was introduced in version 1.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1726
- https://github.com/containers/podman/commit/c140ecdc9b416ab4efd4d21d14acd63b6adbdd42
- https://access.redhat.com/errata/RHSA-2020:0680
- https://access.redhat.com/errata/RHSA-2020:1650
- https://access.redhat.com/security/cve/CVE-2020-1726
- https://bugzilla.redhat.com/show_bug.cgi?id=1801152
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1726
- https://github.com/containers/podman
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00097.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00103.html
