# [M] Cube API denial of service attack

## Summary
Severity: Medium
Advisory: GHSA-9759-3276-g2pm
CVE: CVE-2023-50709
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-9759-3276-g2pm
Type: github-advisory

## Affected
- npm: `@cubejs-backend/api-gateway` — affected >=0 <0.34.34

## Details
### Impact
It is possible to make the entire Cube API unavailable by submitting a specially crafted request to a Cube API endpoint.

### Patches
The issue has been patched in the `v0.34.34` and it's recommended that all users exposing Cube APIs to the public internet upgrade to the latest version to prevent service disruption.

### Workarounds
There are currently no workaround for older versions, and the recommendation is to upgrade.

### References
The issue was reported by [y0d3n](https://github.com/y0d3n) in our Community Slack and has been promptly patched in the recent update.

## References
- https://github.com/cube-js/cube/security/advisories/GHSA-9759-3276-g2pm
- https://nvd.nist.gov/vuln/detail/CVE-2023-50709
- https://github.com/cube-js/cube
- https://github.com/cube-js/cube/releases/tag/v0.34.34
