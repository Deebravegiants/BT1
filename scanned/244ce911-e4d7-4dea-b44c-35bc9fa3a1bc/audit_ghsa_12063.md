# [H] Parse Server has a query condition depth bypass via pre-validation transform pipeline

## Summary
Severity: High
Advisory: GHSA-9fjp-q3c4-6w3j
CVE: CVE-2026-33498
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-9fjp-q3c4-6w3j
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.44
- npm: `parse-server` — affected >=0 <8.6.55

## Details
### Impact

An attacker can send an unauthenticated HTTP request with a deeply nested query containing logical operators to permanently hang the Parse Server process. The server becomes completely unresponsive and must be manually restarted. This is a bypass of the fix for CVE-2026-32944.

### Patches

The query condition nesting depth is now validated before the query enters the transformation pipeline, preventing deeply nested structures from being recursively processed before the existing depth guard can fire.

### Workarounds

None.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-9fjp-q3c4-6w3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33498
- https://github.com/parse-community/parse-server/pull/10257
- https://github.com/parse-community/parse-server/pull/10258
- https://github.com/parse-community/parse-server/commit/2581b5426047ce9cbcd3d9c0e8379e9c30e23ab5
- https://github.com/parse-community/parse-server/commit/85994eff9e7b34cac7e1a2f5791985022a1461d1
- https://github.com/parse-community/parse-server
