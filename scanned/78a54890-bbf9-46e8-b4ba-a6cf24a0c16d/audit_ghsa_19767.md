# [M] Laravel framework susceptible to reflected cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-546h-56qp-8jmw
CVE: CVE-2024-13918
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-546h-56qp-8jmw
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=11.9.0 <11.36.0

## Details
The Laravel framework versions between 11.9.0 and 11.35.1 are susceptible to reflected cross-site scripting due to an improper encoding of request parameters in the debug-mode error page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-13918
- https://github.com/laravel/framework/pull/53869
- https://github.com/laravel/framework/commit/45287fb2a91c69bb1c110539b9b7341faf5aee33
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/CVE-2024-13918.yaml
- https://github.com/laravel/framework
- https://github.com/laravel/framework/releases/tag/v11.36.0
- https://github.com/sbaresearch/advisories/tree/public/2024/SBA-ADV-20241209-01_Laravel_Reflected_XSS_via_Request_Parameter_in_Debug-Mode_Error_Page
- http://www.openwall.com/lists/oss-security/2025/03/10/3
