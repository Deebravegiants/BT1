# [C] IDURAR ERP CRM through 4.1.1 Account Takeover via Unverified Identifier on Password Update

## Summary
Severity: Critical
Advisory: CVE-2026-81031
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-81031
Type: osv

## Details
IDURAR ERP CRM changes the password of whichever account a request names rather than the account making the request. The update handler in backend/src/controllers/middlewaresControllers/createUserController/updatePassword.js resolves the authenticated user from the request that the token middleware populated, then issues its update against a filter built from the identifier in the URL path, and never compares the two. The route is mounted behind the administrator token check only, so any valid administrator session is sufficient, and the sole ownership-like guard in the handler rejects a single hardcoded demo address. A caller can therefore set an arbitrary password on any other administrator account and sign in as it. The read handler in the same controller directory accepts an identifier the same way, which supplies the identifiers needed to pick a target.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81031.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81031
- https://www.vulncheck.com/advisories/idurar-erp-crm-through-4.1.1-account-takeover-via-unverified-identifier-on-password-update
- https://github.com/idurar/idurar-erp-crm/issues/1470
- https://github.com/idurar/idurar-erp-crm
- https://github.com/idurar/idurar-erp-crm/blob/4.1.0/backend/src/controllers/middlewaresControllers/createUserController/updatePassword.js
