# [M] Directus' exact version number is exposed by the OpenAPI Spec

## Summary
Severity: Medium
Advisory: GHSA-rmjh-cf9q-pv7q
CVE: CVE-2025-53887
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-rmjh-cf9q-pv7q
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.9.0

## Details
### Summary

The exact Directus version number is incorrectly being used as OpenAPI Spec version this means that it is being exposed by the `/server/specs/oas` endpoint without authentication. 

### Impact

With the exact version information a malicious attacker can look for known vulnerabilities in Directus core or any of its shipped dependencies in that specific running version.

## References
- https://github.com/directus/directus/security/advisories/GHSA-rmjh-cf9q-pv7q
- https://nvd.nist.gov/vuln/detail/CVE-2025-53887
- https://github.com/directus/directus/pull/25353
- https://github.com/directus/directus/commit/e74f3e4e92edc33b5f83eefb001a3d2a85af17a3
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v11.9.0
