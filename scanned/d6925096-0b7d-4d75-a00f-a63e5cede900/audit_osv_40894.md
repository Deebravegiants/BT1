# [H] Cap-go - OTP Bypass via Response Manipulation in Email Verification

## Summary
Severity: High
Advisory: CVE-2026-56073
Aliases: GHSA-x2gq-85v8-j9v4
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-56073
Type: osv

## Details
Cap-go before 12.128.2 contains an authentication bypass vulnerability in OTP verification that allows attackers to bypass email verification by modifying server responses. Attackers can intercept OTP verification requests and manipulate HTTP responses to falsely mark verification successful, enabling unauthorized 2FA enablement and account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56073.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-x2gq-85v8-j9v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56073
- https://www.vulncheck.com/advisories/cap-go-otp-bypass-via-response-manipulation-in-email-verification
