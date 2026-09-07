# [H] Podman Path Traversal Vulnerability leads to arbitrary file read/write

## Summary
Severity: High
Advisory: GHSA-rh5f-2w6r-q7vj
CVE: CVE-2019-10152
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rh5f-2w6r-q7vj
Type: github-advisory

## Affected
- Go: `github.com/containers/podman` — affected >=0 <1.4.0

## Details
A path traversal vulnerability has been discovered in podman before version 1.4.0 in the way it handles symlinks inside containers. An attacker who has compromised an existing container can cause arbitrary files on the host filesystem to be read/written when an administrator tries to copy a file from/to the container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10152
- https://github.com/containers/libpod/issues/3211
- https://github.com/containers/libpod/pull/3214
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10152
- https://github.com/containers/libpod
- https://github.com/containers/libpod/blob/master/RELEASE_NOTES.md#140
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00001.html
