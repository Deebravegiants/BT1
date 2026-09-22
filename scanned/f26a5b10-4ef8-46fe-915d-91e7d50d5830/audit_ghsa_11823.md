# [H] BuildKit's Malicious frontend can cause file escape outside of storage root

## Summary
Severity: High
Advisory: GHSA-4c29-8rgm-jvjj
CVE: CVE-2026-33747
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-4c29-8rgm-jvjj
Type: github-advisory

## Affected
- Go: `github.com/moby/buildkit` — affected >=0 <0.28.1

## Details
### Impact
When using a custom BuildKit frontend, the frontend can craft an API message that causes files to be written outside of the BuildKit state directory for the execution context.

### Patches
The issue has been fixed in v0.28.1+

### Workarounds
Issue requires using an untrusted BuildKit frontend set with `#syntax` or `--build-arg BUILDKIT_SYNTAX`. Using these options with a well-known frontend image like `docker/dockerfile` is not affected.

## References
- https://github.com/moby/buildkit/security/advisories/GHSA-4c29-8rgm-jvjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33747
- https://github.com/moby/buildkit
- https://github.com/moby/buildkit/releases/tag/v0.28.1
