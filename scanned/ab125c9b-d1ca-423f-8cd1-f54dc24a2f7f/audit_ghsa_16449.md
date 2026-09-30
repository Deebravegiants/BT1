# [M] Uptime Kuma's authenticated path traversal via plugin repository name may lead to unavailability or data loss

## Summary
Severity: Medium
Advisory: GHSA-vr8x-74pm-6vj7
CVE: CVE-2023-36822
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-01
Source: https://github.com/advisories/GHSA-vr8x-74pm-6vj7
Type: github-advisory

## Affected
- npm: `uptime-kuma` — affected >=0 <1.22.1

## Details
### Summary
A path traversal vulnerability via the plugin repository name allows an authenticated attacker to delete files on the server leading to unavailability and potentially data loss.

### Details
Uptime Kuma allows authenticated users to install plugins from an official list of plugins. This feature is currently disabled in the web interface, but the corresponding API endpoints are still available after login.
Before a plugin is downloaded, the plugin installation directory is checked for existence. If it exists, it's removed before the plugin installation.

Because the plugin is not validated against the official list of plugins or sanitized, the check for existence and the removal of the plugin installation directory are prone to path traversal.

### Impact
This vulnerability allows an authenticated attacker to delete files from the server Uptime Kuma is running on.
Depending on which files are deleted, Uptime Kuma or the whole system may become unavailable due to data loss.

## References
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-vr8x-74pm-6vj7
- https://nvd.nist.gov/vuln/detail/CVE-2023-36822
- https://github.com/louislam/uptime-kuma/pull/3346
- https://github.com/louislam/uptime-kuma/commit/a0736e04b2838aae198c2110db244eab6f87757b
- https://github.com/louislam/uptime-kuma
- https://github.com/louislam/uptime-kuma/blob/de74efb2e6601dcbcfed32cddefc4078a80fcb0b/server/plugins-manager.js#L75-L80
- https://github.com/louislam/uptime-kuma/releases/tag/1.22.1
