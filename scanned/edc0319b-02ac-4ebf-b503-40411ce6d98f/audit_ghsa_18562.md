# [M] Directus' insufficient permission checks can enable unauthenticated users to manually trigger Flows

## Summary
Severity: Medium
Advisory: GHSA-7cvf-pxgp-42fc
CVE: CVE-2025-53889
CWE: CWE-285, CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-7cvf-pxgp-42fc
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.9.0

## Details
### Summary

Directus Flows with a manual trigger are not validating whether the user triggering the Flow has permissions to the items provided as payload to the Flow. Depending on what the Flow is set up to do this can lead to the Flow executing potential tasks on the attacker's behalf without authenticating.

### Impact

Bad actors could execute the manual trigger Flows without authentication, or access rights to the said collection(s) or item(s).

Users with manual trigger Flows configured are impacted as these endpoints do not currently validate if the user has read access to `directus_flows` or to the relevant collection/items. The manual trigger Flows should have tighter security requirements as compared to webhook Flows where users are expected to perform do their own checks.

### Workarounds
Users have to implement permission checks for read access to Flows and read access to relevant collection/items.

## References
- https://github.com/directus/directus/security/advisories/GHSA-7cvf-pxgp-42fc
- https://nvd.nist.gov/vuln/detail/CVE-2025-53889
- https://github.com/directus/directus/commit/22be460c76957708d67fdd52846a9ad1cbb083fb
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v11.9.0
