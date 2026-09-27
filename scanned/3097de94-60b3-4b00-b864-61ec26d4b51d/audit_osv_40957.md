# [M] Capgo - Unauthenticated API Key Metadata Disclosure via SECURITY DEFINER RPC Function

## Summary
Severity: Medium
Advisory: CVE-2026-56303
Aliases: GHSA-2xjq-h43m-592f
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/CVE-2026-56303
Type: osv

## Details
Capgo before 12.128.2 contains an information disclosure vulnerability in the find_apikey_by_value PostgreSQL function marked SECURITY DEFINER and executable by the anon role. Unauthenticated attackers can call this function via the /rest/v1/rpc/find_apikey_by_value endpoint to retrieve sensitive API key metadata including user_id, mode, org scoping, and expiration details when supplied a valid key value.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56303.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-2xjq-h43m-592f
- https://nvd.nist.gov/vuln/detail/CVE-2026-56303
- https://www.vulncheck.com/advisories/capgo-unauthenticated-api-key-metadata-disclosure-via-security-definer-rpc-function
