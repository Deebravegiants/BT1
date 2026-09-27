# [H] macrozheng mall <= 1.0.3 Unauthenticated Password Reset via OTP Disclosure

## Summary
Severity: High
Advisory: CVE-2026-25858
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-07
Source: https://osv.dev/vulnerability/CVE-2026-25858
Type: osv

## Details
macrozheng mall version 1.0.3 and prior contains an authentication vulnerability in the mall-portal password reset workflow that allows an unauthenticated attacker to reset arbitrary user account passwords using only a victim’s telephone number. The password reset flow exposes the one-time password (OTP) directly in the API response and validates password reset requests solely by comparing the provided OTP to a value stored by telephone number, without verifying user identity or ownership of the telephone number. This enables remote account takeover of any user with a known or guessable telephone number.

## References
- https://www.macrozheng.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25858.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25858
- https://www.vulncheck.com/advisories/macrozheng-mall-unauthenticated-password-reset-via-otp-disclosure
- https://github.com/macrozheng/mall/issues/946
- https://github.com/macrozheng/mall
