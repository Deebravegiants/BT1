# [M] Snipe-IT Vulnerable to Unauthorized Asset Request Cancellation via Unguarded cancel_by_admin Parameter

## Summary
Severity: Medium
Advisory: GHSA-53jc-27pc-x8r8
CVE: CVE-2026-55476
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-53jc-27pc-x8r8
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.0

## Details
### Impact
The route POST `/account/request/{itemType}/{itemId}/{cancel_by_admin?}/{requestingUser?}` accepts `cancel_by_admin` as a plain URL path segment with no authorization check. Any authenticated user regardless of permissions can set this parameter to a truthy value and supply a victim's user ID to silently cancel that user's pending asset requests. The attacker only needs an active session; no elevated privilege is required.

### Patches
Patched in 8.6.1

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-53jc-27pc-x8r8
- https://nvd.nist.gov/vuln/detail/CVE-2026-55476
- https://github.com/grokability/snipe-it/commit/3c1b18919afbba12d419a9795929493b0391c91a
- https://github.com/grokability/snipe-it/commit/ac2162113d9e25e4c61b61916ce67fb2a1050553
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.0
