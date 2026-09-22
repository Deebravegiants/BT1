# [C] Crossplane: Signature verification TOCTOU allows installing unverified package content via mutable tag

## Summary
Severity: Critical
Advisory: GHSA-wfqx-gjrf-g28r
CWE: CWE-345, CWE-367
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-wfqx-gjrf-g28r
Type: github-advisory

## Affected
- Go: `github.com/crossplane/crossplane/v2` — affected >=2.3.0-rc.0
- Go: `github.com/crossplane/crossplane/v2` — affected >=0
- Go: `github.com/crossplane/crossplane` — affected >=0

## Details
## Summary

Crossplane allows package signature verification to be configured via the `ImageConfig` mechanism. When enabled, the package manager uses cosign to verify that packages are correctly signed before pulling and installing them.

When a package is installed using a tag reference (e.g., a semantic version), a malicious OCI registry could serve a correctly signed image for verification, then subsequently serve an unsigned image for installation. This is possible because Crossplane resolves the tag reference separately for each step.

This vulnerability is relevant only for users who do all three of the following:

1. Configure signature verification for packages,
2. Install packages using tag references rather than digests, and
3. Install packages from registries they do not control.

## Mitigation

Installing packages by image digest rather than using tags avoids this issue.

## Fix

The package manager has been updated to resolve tag references once and use the resulting digest for both signature verification and image fetching. This ensures that Crossplane pulls the same content that had its signature verified. The fix has been applied to Crossplane's `main` branch and backported to the v2.3 and v2.2 release branches; it will be released in v2.3.3 and v2.2.3.

## Credits

This issue was reported, independently, by @bugbunny-research and @tonghuaroot.

## References
- https://github.com/crossplane/crossplane/security/advisories/GHSA-wfqx-gjrf-g28r
- https://github.com/crossplane/crossplane
