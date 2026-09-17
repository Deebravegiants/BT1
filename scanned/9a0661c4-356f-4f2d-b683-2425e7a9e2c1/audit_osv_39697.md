# [H] SolidInvoice: API tokens stored as plaintext in the database allowing full credential compromise on database breach

## Summary
Severity: High
Advisory: CVE-2026-46622
Aliases: GHSA-qjfc-h39r-cgwq
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-46622
Type: osv

## Details
SolidInvoice is an open-source invoicing platform. Prior to version 2.3.17, API tokens used to authenticate all REST API requests are stored as plaintext strings in the api_tokens database table. Any attacker who obtains read access to the database — through SQL injection, a leaked backup, a misconfigured replica, or insider access — immediately obtains all API credentials for every user with no further effort. This issue has been patched in version 2.3.17.

## References
- https://github.com/SolidInvoice/SolidInvoice/releases/tag/2.3.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46622.json
- https://github.com/SolidInvoice/SolidInvoice/security/advisories/GHSA-qjfc-h39r-cgwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-46622
- https://github.com/SolidInvoice/SolidInvoice/commit/864539182572e1a3b2d76999b03060661ffa00f1
