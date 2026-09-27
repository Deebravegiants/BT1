# [C] Buildkit's interactive containers API does not validate entitlements check

## Summary
Severity: Critical
Advisory: GHSA-wr6v-9f75-vh2g
CVE: CVE-2024-23653
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-wr6v-9f75-vh2g
Type: github-advisory

## Affected
- Go: `github.com/moby/buildkit` — affected >=0 <0.12.5

## Details
### Impact
In addition to running containers as build steps, BuildKit also provides APIs for running interactive containers based on built images. It was possible to use these APIs to ask BuildKit to run a container with elevated privileges. Normally, running such containers is only allowed if special `security.insecure` entitlement is enabled both by buildkitd configuration and allowed by the user initializing the build request.

### Patches
The issue has been fixed in v0.12.5 .

### Workarounds
Avoid using BuildKit frontends from untrusted sources. A frontend image is usually specified as the `#syntax` line on your Dockerfile, or with `--frontend` flag when using `buildctl build` command.

### References

## References
- https://github.com/moby/buildkit/security/advisories/GHSA-wr6v-9f75-vh2g
- https://nvd.nist.gov/vuln/detail/CVE-2024-23653
- https://github.com/moby/buildkit/pull/4602
- https://github.com/moby/buildkit/commit/5026d95aa3336e97cfe46e3764f52d08bac7a10e
- https://github.com/moby/buildkit/commit/92cc595cfb12891d4b3ae476e067c74250e4b71e
- https://github.com/moby/buildkit
- https://github.com/moby/buildkit/releases/tag/v0.12.5
