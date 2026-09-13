# [M] Snipe-IT's selectlist visibility is too permissive

## Summary
Severity: Medium
Advisory: GHSA-f3c5-6cw8-fg57
CVE: CVE-2026-48492
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-f3c5-6cw8-fg57
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.5.1

## Details
### Impact
The GET /api/v1/{object}/selectlist API endpoint is missing an authorization check. Any user who can log into Snipe-IT - regardless of permissions - can retrieve a paginated list of all user accounts using only their web session cookie. No API token or elevated permissions are required. This exposes usernames, display names, employee numbers, and user IDs for every active account in the system if FMCS is not enabled, and within the company they belong to if FMCS is enabled.

### What an attacker can do with a valid login and zero permissions:
- Enumerate all active user accounts by paginating through the endpoint
- Harvest usernames for credential stuffing or password spray attacks
- Collect employee numbers and full names for social engineering
- Perform indirect email enumeration via the search parameter
- Map user IDs for use in further enumeration against other endpoints

This vulnerability is exploitable only by users who have a working login to the Snipe-IT system. 

### Patches
https://github.com/grokability/snipe-it/commit/4f943d4a7ab8e53f3d9e32770602d1118bab005f

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-f3c5-6cw8-fg57
- https://github.com/grokability/snipe-it/commit/4f943d4a7ab8e53f3d9e32770602d1118bab005f
- https://github.com/grokability/snipe-it
