# [C] @valtimo/components exposes access token to form.io

## Summary
Severity: Critical
Advisory: GHSA-xcp4-62vj-cq3r
CVE: CVE-2024-34706
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-xcp4-62vj-cq3r
Type: github-advisory

## Affected
- npm: `@valtimo/components` — affected >=0 <10.8.4
- npm: `@valtimo/components` — affected >=11.0.0 <11.1.6
- npm: `@valtimo/components` — affected >=11.2.0 <11.2.2

## Details
### Impact
When opening a form in Valtimo, the access token (JWT) of the user is exposed to `api.form.io` via the the `x-jwt-token` header. An attacker can retrieve personal information from this token, or use it to execute requests to the Valtimo REST API on behalf of the logged-in user.

This issue is caused by a misconfiguration of the Form.io component.

### Attack requirements ###
The following conditions have to be met in order to perform this attack:
- An attacker needs to have access to the network traffic on the `api.form.io` domain.
- The content of the `x-jwt-token` header is logged or otherwise available to the attacker.
- An attacker needs to have network access to the Valtimo API.
- An attacker needs to act within the time-to-live of the access token. The default TTL in Keycloak is 5 minutes.

### Patches
Versions 10.8.4, 11.1.6 and 11.2.2 have been patched

## References
- https://github.com/valtimo-platform/valtimo-frontend-libraries/security/advisories/GHSA-xcp4-62vj-cq3r
- https://nvd.nist.gov/vuln/detail/CVE-2024-34706
- https://github.com/valtimo-platform/valtimo-frontend-libraries/commit/1aaba5ef5750dafebbc7476fb08bf2375a25f19e
- https://github.com/valtimo-platform/valtimo-frontend-libraries/commit/8c2dbf2a41180d2b0358d878290e4d37168f0fb6
- https://github.com/valtimo-platform/valtimo-frontend-libraries/commit/d65e05fd2784bd4a628778b34a5b79ce2f0cef8c
- https://github.com/valtimo-platform/valtimo-frontend-libraries
