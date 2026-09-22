# [H] BuildKit vulnerable to possible race condition with accessing subpaths from cache mounts

## Summary
Severity: High
Advisory: GHSA-m3r6-h7wv-7xxv
CVE: CVE-2024-23651
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-m3r6-h7wv-7xxv
Type: github-advisory

## Affected
- Go: `github.com/moby/buildkit` — affected >=0 <0.12.5

## Details
### Impact
Two malicious build steps running in parallel sharing the same cache mounts with subpaths could cause a race condition that can lead to files from the host system being accessible to the build container.

### Patches
The issue has been fixed in v0.12.5

### Workarounds
Avoid using BuildKit frontend from an untrusted source or building an untrusted Dockerfile containing cache mounts with `--mount=type=cache,source=...` options.

### References
https://www.openwall.com/lists/oss-security/2019/05/28/1

## References
- https://github.com/moby/buildkit/security/advisories/GHSA-m3r6-h7wv-7xxv
- https://nvd.nist.gov/vuln/detail/CVE-2024-23651
- https://github.com/moby/buildkit/pull/4604
- https://github.com/moby/buildkit
- https://github.com/moby/buildkit/releases/tag/v0.12.5
