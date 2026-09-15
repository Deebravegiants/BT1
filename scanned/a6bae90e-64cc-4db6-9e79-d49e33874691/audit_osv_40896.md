# [M] Cap-go - Authentication Logic Flaw in Enforce Password Policy

## Summary
Severity: Medium
Advisory: CVE-2026-56080
Aliases: GHSA-78rv-3cqj-36xq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-56080
Type: osv

## Details
Capgo before 12.128.2 contains a flaw in the Enforce Password Policy feature: after a Super Admin enables the policy and successfully changes their password to a compliant one, the backend does not update the password-compliance state. As a result, the backend continues to treat the account as non-compliant and repeatedly forces password-reset prompts, permanently locking the Super Admin out of organization access (organization lockout / denial of service) despite valid authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56080.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-78rv-3cqj-36xq
- https://nvd.nist.gov/vuln/detail/CVE-2026-56080
- https://www.vulncheck.com/advisories/cap-go-authentication-logic-flaw-in-enforce-password-policy
