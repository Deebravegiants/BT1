# [M] Directus version number disclosure

## Summary
Severity: Medium
Advisory: GHSA-5mhg-wv8w-p59j
CVE: CVE-2024-27296
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-03-01
Source: https://github.com/advisories/GHSA-5mhg-wv8w-p59j
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <10.8.3

## Details
### Impact

Currently the exact Directus version number is being shipped in compiled JS bundles which are accessible without authentication. With this information a malicious attacker can trivially look for known vulnerabilities in Directus core or any of its shipped dependencies in that specific running version.

### Patches

The problem has been resolved in versions 10.8.3 and newer

### Workarounds

None

## References
- https://github.com/directus/directus/security/advisories/GHSA-5mhg-wv8w-p59j
- https://nvd.nist.gov/vuln/detail/CVE-2024-27296
- https://github.com/directus/directus/commit/a5a1c26ac48795ed3212a4c51b9523588aff4fa0
- https://github.com/directus/directus
