# [M] Missing authorization in Prospero Flow CRM allows low-privileged users to read all bank accounts

## Summary
Severity: Medium
Advisory: CVE-2026-59235
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-59235
Type: osv

## Details
Missing Authorization (CWE-862) in BankAccountListController (app/Http/Controllers/Api/BankAccount/BankAccountListController.php), exposed at GET /api/bank-account, in Prospero Flow CRM <5.5.3, which allows a remote, authenticated attacker holding a low-privileged role (e.g. the "User"/"Usuario" role) to read arbitrary bank account records belonging to their company by sending an authenticated request to the endpoint with a valid bearer token, because the API route is protected only by the auth:api middleware and carries no permission gate, unlike the equivalent web route, which enforces can('read bank'), and the handler resolves records with Account::where('company_id', Auth::user()->company_id)->get(), performing only company scoping and no role or permission check before returning the data. This results in the unauthorized disclosure of sensitive banking information (e.g. IBAN, SWIFT/BIC, account identifiers) to users who should not have access to it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59235.json
- https://github.com/Roskus/prospero-flow-crm/releases#release-v5.5.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-59235
- https://github.com/Roskus/prospero-flow-crm/commit/57bb57212af03151c989d67d6723d5ddb3e81e7b
- https://github.com/Roskus/prospero-flow-crm
- https://secur0.com/en/cna/cve-list/cve-2026-59235-missing-authorization-in-prospero-flow-crm-allows-low-privileged-users-to-read-all-bank-accounts
