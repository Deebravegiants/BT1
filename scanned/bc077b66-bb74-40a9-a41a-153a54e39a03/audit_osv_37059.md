# [M] Packistry accepts expired access tokens

## Summary
Severity: Medium
Advisory: CVE-2026-27968
Aliases: GHSA-4r9m-jp53-vgmw
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27968
Type: osv

## Details
Packistry is a self-hosted Composer repository designed to handle PHP package distribution. Prior to version 0.13.0, RepositoryAwareController::authorize() verified token presence and ability, but did not enforce token expiration. As a result, an expired deploy token with the correct ability could still access repository endpoints (e.g., Composer metadata/download APIs). The fix in version 0.13.0 adds an explicit expiration check, and tests now test expired deploy tokens to ensure they are rejected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27968.json
- https://github.com/packistry/packistry/security/advisories/GHSA-4r9m-jp53-vgmw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27968
- https://github.com/packistry/packistry/commit/7740b48f0f4ecbe63099fb056c8a146180f8b283
- https://github.com/packistry/packistry/pull/276
