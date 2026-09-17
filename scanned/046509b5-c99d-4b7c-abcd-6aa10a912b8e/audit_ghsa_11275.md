# [H] FUXA has a hardcoded fallback JWT signing secret

## Summary
Severity: High
Advisory: GHSA-c8m8-3jcr-6rj5
CVE: CVE-2025-69971
CWE: CWE-321, CWE-798
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-c8m8-3jcr-6rj5
Type: github-advisory

## Affected
- npm: `@frangoteam/fuxa` — affected >=0 <1.3.0

## Details
FUXA used a static fallback JWT signing secret (`frangoteam751`) when no `secretCode` was configured.

If authentication was enabled without explicitly setting a custom secret, an attacker who knew the default value could forge valid JWT tokens and bypass authentication.

This issue has been addressed in version 1.3.0 by removing the static fallback and generating a secure random secret when no `secretCode` is provided.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-c8m8-3jcr-6rj5
- https://nvd.nist.gov/vuln/detail/CVE-2025-69971
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/blob/master/server/api/jwt-helper.js
