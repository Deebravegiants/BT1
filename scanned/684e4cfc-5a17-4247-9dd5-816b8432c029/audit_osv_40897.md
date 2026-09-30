# [H] Cap-go - Account Lockout via 2FA Misconfiguration on Unverified Email

## Summary
Severity: High
Advisory: CVE-2026-56081
Aliases: GHSA-j4cx-5pw6-5v5j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-56081
Type: osv

## Details
Cap-go before 12.128.2 contains an authentication logic flaw that lets an attacker register and control an account bound to a victim's email address before that email is verified. By enabling two-factor authentication on the pre-registered account, the attacker gains control over the account claimed under the victim's identity, allowing them to read and modify its state and enforce organization-level policies, while the legitimate user is denied access to the account tied to their own email.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56081.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-j4cx-5pw6-5v5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-56081
- https://www.vulncheck.com/advisories/cap-go-account-lockout-via-2fa-misconfiguration-on-unverified-email
