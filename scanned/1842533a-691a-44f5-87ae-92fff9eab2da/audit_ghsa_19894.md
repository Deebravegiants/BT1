# [M] API Platform Core does not call GraphQl securityAfterResolver

## Summary
Severity: Medium
Advisory: GHSA-7mxx-3cgm-xxv3
CVE: CVE-2025-23204
CWE: CWE-20, CWE-484
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-7mxx-3cgm-xxv3
Type: github-advisory

## Affected
- Packagist: `api-platform/core` — affected >=3.3.8 <3.3.15

## Details
### Summary
A security check that gets called after GraphQl resolvers is always replaced by another one as there's no break in this clause: https://github.com/api-platform/core/pull/6444/files#diff-09e3c2cfe12a2ce65bd6c983c7ca6bfcf783f852b8d0554bb938e8ebf5e5fa65R56

https://github.com/soyuka/core/blob/7e2e8f9ff322ac5f6eb5f65baf432bffdca0fd51/src/Symfony/Security/State/AccessCheckerProvider.php#L49-L57 

### PoC

Create a graphql endpoint with a security after resolver.

### Impact

As this fallsback to `security`, the impact is there only when there's only a security after resolver and none inside security. The test at https://github.com/api-platform/core/pull/6444 is probably broken.

## References
- https://github.com/api-platform/core/security/advisories/GHSA-7mxx-3cgm-xxv3
- https://nvd.nist.gov/vuln/detail/CVE-2025-23204
- https://github.com/api-platform/core/pull/6444
- https://github.com/api-platform/core/pull/6444/files#diff-09e3c2cfe12a2ce65bd6c983c7ca6bfcf783f852b8d0554bb938e8ebf5e5fa65R56
- https://github.com/api-platform/core/commit/dc4fc84ba93e22b4f44a37e90a93c6d079c1c620
- https://github.com/api-platform/core
- https://github.com/soyuka/core/blob/7e2e8f9ff322ac5f6eb5f65baf432bffdca0fd51/src/Symfony/Security/State/AccessCheckerProvider.php#L49-L57
