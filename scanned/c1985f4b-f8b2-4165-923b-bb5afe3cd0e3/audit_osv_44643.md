# [H] Missing Rate Limiting in Email OTP Verification Allows Brute-Force Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2026-85237
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:L/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85237
Type: osv

## Details
A vulnerability in MISP's email-based one-time password (OTP) authentication flow allowed an attacker to perform an unrestricted number of OTP verification attempts.


The email_otp() endpoint did not apply brute-force protection when validating submitted OTP values. An attacker who had reached the OTP verification stage, for example after successfully providing a user's primary authentication credentials, could repeatedly submit candidate OTP values while the same OTP remained valid. This significantly increased the feasibility of guessing the OTP and bypassing the additional authentication factor, potentially resulting in unauthorized access to the affected user's account.


The issue was exacerbated by the fact that the OTP is associated with the user rather than with an individual pending login session, allowing multiple concurrent sessions to attempt guesses against the same valid OTP.


The patch integrates the existing MISP brute-force protection mechanism into the email OTP flow. Failed OTP attempts are now counted against the user, further attempts are rejected once the configured threshold is reached, and the active OTP is invalidated when the attempt budget is exhausted. Blocklisted users are also prevented from requesting the generation of a fresh OTP. In addition, OTP comparison now uses hash_equals() and validates that the submitted value is a string.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85237.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85237
- https://github.com/MISP/MISP/commit/8658062ea
- https://github.com/MISP/MISP
