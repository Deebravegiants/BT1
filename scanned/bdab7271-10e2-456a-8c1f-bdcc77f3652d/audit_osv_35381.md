# [H] Flowise - Unverified Email Change via Account Profile Endpoint

## Summary
Severity: High
Advisory: CVE-2025-71337
Aliases: GHSA-x39m-3393-3qp4
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2025-71337
Type: osv

## Details
Flowise before 3.0.10 (affected versions 3.0.7 and earlier) contains an unverified email change vulnerability. An authenticated user can change the account email address, used as a login identifier and password-recovery channel, via the account profile endpoint without confirming the change to the original email address or re-entering the current password. By changing the recovery email, an attacker can take over the account and abuse password reset mechanisms.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71337.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-x39m-3393-3qp4
- https://nvd.nist.gov/vuln/detail/CVE-2025-71337
- https://www.vulncheck.com/advisories/flowise-unverified-email-change-via-account-profile-endpoint
