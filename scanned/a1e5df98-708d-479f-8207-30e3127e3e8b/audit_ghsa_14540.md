# [M] Podman Time-of-check Time-of-use (TOCTOU) Race Condition

## Summary
Severity: Medium
Advisory: GHSA-qwqv-rqgf-8qh8
CVE: CVE-2023-0778
CWE: CWE-367
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-qwqv-rqgf-8qh8
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v4` — affected >=0 <4.4.2

## Details
A Time-of-check Time-of-use (TOCTOU) flaw was found in podman. This issue may allow a malicious user to replace a normal file in a volume with a symlink while exporting the volume, allowing for access to arbitrary files on the host file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0778
- https://github.com/containers/podman/pull/17528
- https://github.com/containers/podman/pull/17532
- https://github.com/containers/podman/commit/6ca857feb07a5fdc96fd947afef03916291673d8
- https://access.redhat.com/security/cve/CVE-2023-0778
- https://bugzilla.redhat.com/show_bug.cgi?id=2168256
- https://github.com/containers/podman
- https://pkg.go.dev/vuln/GO-2023-1681
