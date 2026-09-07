# [H] TSPortal: Any user can forge self-deletion requests for any account

## Summary
Severity: High
Advisory: GHSA-gfhq-7499-f3f2
CVE: CVE-2026-29788
CWE: CWE-1287, CWE-283
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-gfhq-7499-f3f2
Type: github-advisory

## Affected
- Packagist: `miraheze/ts-portal` — affected >=0 <30

## Details
### Summary
Conversion of empty strings to null allows disguising DPA reports as genuine self-deletion reports.

### Details
Creating a DPA report about another user and leaving the evidence field empty causes that report to look like the reported user self-requested deletion of their data. Ingenuine report is not distinguishable from a genuine one.

This can be prevented by disabling [convertEmptyStringsToNull](https://api.laravel.com/docs/12.x/Illuminate/Foundation/Configuration/Middleware.html#method_convertEmptyStringsToNull) in the middleware, or by validating `evidence` in Http/Controllers/DPAController::store() to not be empty.

### PoC
New DPA report -> Select "...someone who I suspect is under the age of 13" for the "The above username is..." field -> Add nothing to the "Evidence" field -> Submit

### Impact
Potential unauthorized deletion of any arbitrary user's data both in the current system (TSPortal) and subsequent systems if actioned.

## References
- https://github.com/miraheze/TSPortal/security/advisories/GHSA-gfhq-7499-f3f2
- https://nvd.nist.gov/vuln/detail/CVE-2026-29788
- https://api.laravel.com/docs/12.x/Illuminate/Foundation/Configuration/Middleware.html#method_convertEmptyStringsToNull
- https://github.com/miraheze/TSPortal
- https://issue-tracker.miraheze.org/T15053
