# [M] Podman Origin Validation Error

## Summary
Severity: Medium
Advisory: GHSA-grh6-q6m2-rh72
CVE: CVE-2021-20199
CWE: CWE-200, CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-grh6-q6m2-rh72
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v3` — affected >=0 <3.0.0

## Details
Rootless containers run with Podman, receive all traffic with a source IP address of 127.0.0.1 (including from remote hosts). This impacts containerized applications that trust localhost (127.0.01) connections by default and do not require authentication. This issue affects Podman versions from 1.8.0 to 3.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20199
- https://github.com/containers/podman/issues/5138
- https://github.com/containers/podman/pull/9052
- https://github.com/containers/podman/pull/9225
- https://github.com/rootless-containers/rootlesskit/pull/206
- https://bugzilla.redhat.com/show_bug.cgi?id=1919050
- https://github.com/containers/podman/releases/tag/v3.0.0-rc3
