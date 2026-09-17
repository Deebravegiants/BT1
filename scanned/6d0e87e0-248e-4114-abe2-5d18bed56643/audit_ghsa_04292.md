# [H] Snipe-IT API Vulnerable to Cross-Tenant Accessory Injection

## Summary
Severity: High
Advisory: GHSA-pwpj-p52h-q484
CVE: CVE-2026-54329
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-pwpj-p52h-q484
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
A cross-tenant data injection vulnerability was identified in the Snipe-IT Accessories API when Full Multiple Companies Support (FMCS) is enabled. A low-privileged authenticated user belonging to one company can create an accessory record under another company by supplying a foreign company_id value in the API request body.

The issue occurs because the API create path mass-assigns request parameters directly to the Accessory model, and the Accessory model allows company_id to be mass assigned. Unlike the web controller, which uses Company::getIdForCurrentUser() to enforce the authenticated user’s company context, the API controller does not apply equivalent tenant enforcement during accessory creation.

As a result, a Company A user can inject persistent accessory records into Company B. The injected records are then visible to Company B users as legitimate Company B inventory records. This breaks the integrity of company-scoped inventory data and represents a tenant isolation failure in the accessory creation flow.

### Patches
Patched in https://github.com/grokability/snipe-it/commit/dc8cbf4786bb38b260b4ae1723ec9e7f81d82fe5

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-pwpj-p52h-q484
- https://github.com/grokability/snipe-it/commit/dc8cbf4786bb38b260b4ae1723ec9e7f81d82fe5
- https://github.com/grokability/snipe-it
