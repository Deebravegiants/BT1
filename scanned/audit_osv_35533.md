# [M] QueryWeaver Authentication Bypass via Email Signup Token Issuance for Existing Accounts

## Summary
Severity: Medium
Advisory: CVE-2026-10130
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-18
Source: https://osv.dev/vulnerability/CVE-2026-10130
Type: osv

## Details
QueryWeaver contains an authentication bypass vulnerability that allows unauthenticated attackers to obtain valid session tokens for existing accounts by submitting a signup request with a known victim email address. The signup route unconditionally creates and links a new token to the matching Identity via a Cypher MERGE operation before checking whether the email belongs to an existing account, causing the server to return a valid authenticated session token for the victim's identity without requiring any prior credentials or user interaction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10130.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10130
- https://www.vulncheck.com/advisories/queryweaver-authentication-bypass-via-email-signup-token-issuance-for-existing-accounts
- https://github.com/FalkorDB/QueryWeaver/commit/e6a49f508191d0f1bdad0f146da43819e7849f18
- https://github.com/FalkorDB/QueryWeaver
