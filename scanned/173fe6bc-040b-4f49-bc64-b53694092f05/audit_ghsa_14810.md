# [H] Directus is soft-locked by providing a string value to random string util

## Summary
Severity: High
Advisory: GHSA-632p-p495-25m5
CVE: CVE-2024-36128
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-632p-p495-25m5
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <10.11.2

## Details
### Describe the Bug

Providing a non-numeric length value to the random string generation utility will create a memory issue breaking the capability to generate random strings platform wide. This creates a denial of service situation where logged in sessions can no longer be refreshed as sessions depend on the capability to generate a random session ID.

### To Reproduce

1. Test if the endpoint is working and accessible, `GET http://localhost:8055/utils/random/string`
2. Do a bad request `GET http://localhost:8055/utils/random/string?length=foo`
3. After this all calls to `GET http://localhost:8055/utils/random/string` will return an empty string instead of a random string
4. In this error situation you'll see authentication refreshes fail for the app and api.

### Impact

This counts as an unauthenticated denial of service attack vector so this impacts all unpatched instances reachable over the internet.

## References
- https://github.com/directus/directus/security/advisories/GHSA-632p-p495-25m5
- https://nvd.nist.gov/vuln/detail/CVE-2024-36128
- https://github.com/directus/directus/commit/7d2a1392f43613094de700062aba168a9400dd3b
- https://github.com/directus/directus
