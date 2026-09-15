# [M] Buildah (as part of Podman) vulnerable to Link Following

## Summary
Severity: Medium
Advisory: GHSA-4crw-w8pw-2hmf
CVE: CVE-2022-4122
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-08
Source: https://github.com/advisories/GHSA-4crw-w8pw-2hmf
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v4` — affected >=0 <4.5.0

## Details
A vulnerability was found in buildah. Incorrect following of symlinks while reading .containerignore and .dockerignore results in information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4122
- https://github.com/containers/podman/pull/16315
- https://github.com/containers/podman/commit/c8eeab21cf0a4f670be0cd399dd06fd5d4e06dfe
- https://bugzilla.redhat.com/show_bug.cgi?id=2144983
