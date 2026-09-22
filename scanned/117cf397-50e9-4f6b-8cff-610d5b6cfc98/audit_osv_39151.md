# [H] FreePBX: Authenticated Access can lead to Subsequent OAuth2 Authentication Bypass in API Module

## Summary
Severity: High
Advisory: CVE-2026-44237
Aliases: GHSA-vgjf-4h63-8vcc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44237
Type: osv

## Details
FreePBX is an open source IP PBX. Prior to 17.0.8, the FreePBX api module's OAuth2 implementation does not sufficiently validate client credentials during token issuance. Knowledge of a valid client_id is required. The validateClient() method in ClientRepository.php unconditionally returns true, allowing any party with knowledge of a valid client_id to obtain OAuth2 access tokens without providing the correct client_secret. This vulnerability is fixed in 17.0.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44237.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-vgjf-4h63-8vcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44237
