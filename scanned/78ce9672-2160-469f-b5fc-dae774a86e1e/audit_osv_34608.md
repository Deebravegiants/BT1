# [H] Matrix Authentication Service account password can be changed using an authenticated session without supplying the current password

## Summary
Severity: High
Advisory: CVE-2025-62425
Aliases: GHSA-6wfp-jq3r-j9xh
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-62425
Type: osv

## Details
MAS (Matrix Authentication Service) is a user management and authentication service for Matrix homeservers, written and maintained by Element. A logic flaw in matrix-authentication-service 0.20.0 through 1.4.0 allows an attacker with access to an authenticated MAS session to perform sensitive operations without entering the current password. These include changing the current password, adding or removing an e-mail address and deactivating the account. The vulnerability only affects instances which have the local password database feature enabled (passwords section in the config). Patched in matrix-authentication-service 1.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62425.json
- https://github.com/element-hq/matrix-authentication-service/security/advisories/GHSA-6wfp-jq3r-j9xh
- https://nvd.nist.gov/vuln/detail/CVE-2025-62425
- https://github.com/element-hq/matrix-authentication-service/commit/bce99edb6177be11f8f38c1d01f5606ce7b4b2e5
