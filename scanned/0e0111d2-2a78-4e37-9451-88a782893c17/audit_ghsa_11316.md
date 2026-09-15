# [H] BuildKit Git URL subdir component can cause access to restricted files

## Summary
Severity: High
Advisory: GHSA-4vrq-3vrq-g6gg
CVE: CVE-2026-33748
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-4vrq-3vrq-g6gg
Type: github-advisory

## Affected
- Go: `github.com/moby/buildkit` — affected >=0 <0.28.1

## Details
### Impact
Insufficient validation of Git URL fragment subdir components (`<url>#<ref>:<subdir>`, [docs](https://docs.docker.com/build/concepts/context/#url-fragments)) may allow access to files outside the checked-out Git repository root. Possible access is limited to files on the same mounted filesystem.

### Patches
The issue has been fixed in version v0.28.1

### Workarounds
The issue affects only builds that use Git URLs with a subpath component. Avoid building Dockerfiles from untrusted sources or using the subdir component from an untrusted Git repository where the subdir component could point to a symlink.

## References
- https://github.com/moby/buildkit/security/advisories/GHSA-4vrq-3vrq-g6gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33748
- https://docs.docker.com/build/concepts/context/#url-fragments
- https://github.com/moby/buildkit
- https://github.com/moby/buildkit/releases/tag/v0.28.1
