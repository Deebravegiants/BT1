# [M] Improper Scope Enforcement in OAuth client_credentials Flow Allows Read-Only API Key to Escalate to Full Access

## Summary
Severity: Medium
Advisory: CVE-2026-21621
Aliases: EEF-CVE-2026-21621, GHSA-739m-8727-j6w3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-21621
Type: osv

## Details
Incorrect Authorization vulnerability in hexpm hexpm/hexpm ('Elixir.HexpmWeb.API.OAuthController' module) allows Privilege Escalation.

An API key created with read-only permissions (domain: "api", resource: "read") can be escalated to full write access under specific conditions.

When exchanging a read-only API key via the OAuth client_credentials grant, the resource qualifier is ignored. The resulting JWT receives the broad "api" scope instead of the expected "api:read" scope. This token is therefore treated as having full API access.

If an attacker is able to obtain a victim's read-only API key and a valid 2FA (TOTP) code for the victim account, they can use the incorrectly scoped JWT to create a new full-access API key with unrestricted API permissions that does not expire by default and can perform write operations such as publishing, retiring, or modifying packages.

This vulnerability is associated with program files lib/hexpm_web/controllers/api/oauth_controller.ex and program routines 'Elixir.HexpmWeb.API.OAuthController':validate_scopes_against_key/2.

This issue affects hexpm: from 71829cb6f6559bcceb1ef4e43a2fb8cdd3af654b before 71c127afebb7ed7cc637eb231b98feb802d62999.

## References
- https://cna.erlef.org/cves/CVE-2026-21621.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-21621
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21621.json
- https://github.com/hexpm/hexpm/security/advisories/GHSA-739m-8727-j6w3
- https://nvd.nist.gov/vuln/detail/CVE-2026-21621
- https://github.com/hexpm/hexpm/commit/71c127afebb7ed7cc637eb231b98feb802d62999
- https://github.com/hexpm/hexpm.git
