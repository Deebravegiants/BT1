# [H] Snipe-IT: Chained Information Disclosure and IDOR Leads to Full EULA File Takeover

## Summary
Severity: High
Advisory: GHSA-3hgv-jr5j-cg9x
CVE: CVE-2026-55694
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-3hgv-jr5j-cg9x
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.3

## Details
### Impact
An attacker can completely bypass file-name randomization security and without authorization download confidential, signed EULA files belonging to any other user across the application.

### Steps to Reproduce:
1. Log in as a restricted user.
2. Send a GET request to /api/v1/users/{target_id}/eulas (where target_id belongs to a restricted/denied user).
3. Observe the response leaks the secret EULA filename (e.g., eula-xxx.pdf).
4. Attempt to access this file via the main route: GET /stored-eula-file/{filename} (This will correctly return 403 Forbidden).
5. Now, access the file via the vulnerable profile route: GET /account/stored-eula-file/{filename}.
6. Observe that the server returns a 200 OK and successfully downloads the target user's secret EULA file.

### Patches
Fixed in https://github.com/grokability/snipe-it/commit/f15d78621b003be30ac114ba68626683894935ef

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-3hgv-jr5j-cg9x
- https://github.com/grokability/snipe-it/commit/f15d78621b003be30ac114ba68626683894935ef
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.3
