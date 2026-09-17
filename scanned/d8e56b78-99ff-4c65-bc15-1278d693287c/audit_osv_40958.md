# [H] Capgo - Authentication Bypass in Password Change via Missing Current Password Validation

## Summary
Severity: High
Advisory: CVE-2026-56305
Aliases: GHSA-rjr5-qxqj-cx8g
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-56305
Type: osv

## Details
Capgo before 12.128.2 contains an authentication bypass vulnerability in the password change endpoint that allows attackers to change user passwords without requiring current password confirmation. Attackers with temporary session access can exploit this flaw to permanently lock out legitimate users and achieve full account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56305.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-rjr5-qxqj-cx8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-56305
- https://www.vulncheck.com/advisories/capgo-authentication-bypass-in-password-change-via-missing-current-password-validation
