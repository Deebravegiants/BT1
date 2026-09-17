# [M] Build breakout using malicious Containerfile and Git Smart HTTP server or GitHub release tar archive

## Summary
Severity: Medium
Advisory: GHSA-49p4-px3h-rq49
CVE: CVE-2026-44517
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-49p4-px3h-rq49
Type: github-advisory

## Affected
- Go: `github.com/containers/buildah` — affected >=1.38.1 <1.43.2

## Details
### Impact

When processing a build contexts or `add`/`copy` instructions, a malicious server serving a Git repository or a tar archive file can cause files outside of the build context directory to be included in the build context or copied into the build.

### Patches

Fixed in Buildah 1.44 and 1.43.2.

## References
- https://github.com/containers/buildah/security/advisories/GHSA-49p4-px3h-rq49
- https://github.com/podman-container-tools/buildah/security/advisories/GHSA-49p4-px3h-rq49
- https://github.com/podman-container-tools/buildah
