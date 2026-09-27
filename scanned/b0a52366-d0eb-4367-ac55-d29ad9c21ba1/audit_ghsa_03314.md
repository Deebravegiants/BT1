# [H] Improper Authorization in github.com/containers/libpod

## Summary
Severity: High
Advisory: GHSA-9h63-7qf6-mv6r
CVE: CVE-2021-20188
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-9h63-7qf6-mv6r
Type: github-advisory

## Affected
- Go: `github.com/containers/libpod` — affected >=0 <1.7.0

## Details
A flaw was found in podman before 1.7.0. File permissions for non-root users running in a privileged container are not correctly checked. This flaw can be abused by a low-privileged user inside the container to access any other file in the container, even if owned by the root user inside the container. It does not allow to directly escape the container, though being a privileged container means that a lot of security features are disabled when running the container. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20188
- https://github.com/containers/podman/commit/2c7b579fe7328dc6db48bdaf60d0ddd9136b1e24
- https://github.com/containers/podman/commit/c8bd4746151e6ae37d49c4688f2f64e03db429fc
- https://github.com/containers/podman/commit/dcf3c742b1ac4d641d66810113f3d17441a412f4
- https://bugzilla.redhat.com/show_bug.cgi?id=1915734
