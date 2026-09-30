# [M] Capgo - Unauthenticated API Key Validity Oracle and User Identity Disclosure via get_identity_apikey_only RPC

## Summary
Severity: Medium
Advisory: CVE-2026-56242
Aliases: GHSA-fhgj-7376-qxwx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-56242
Type: osv

## Details
Capgo before 12.128.2 contains an unauthenticated security definer RPC function get_identity_apikey_only that returns the owning user_id for supplied API keys, creating an API key validity oracle and user identity disclosure primitive. Attackers can call this endpoint with valid or invalid API keys to confirm key validity and map keys to user identifiers, then chain results into other exposed RPCs like get_orgs_v6 to retrieve organization membership and management email PII.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56242.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-fhgj-7376-qxwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-56242
- https://www.vulncheck.com/advisories/capgo-unauthenticated-api-key-validity-oracle-and-user-identity-disclosure-via-get-identity-apikey-only-rpc
