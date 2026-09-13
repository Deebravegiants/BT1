# [M] Parse Server: MFA SMS one-time password accepted twice under concurrent login

## Summary
Severity: Medium
Advisory: BIT-parse-2026-43930
Aliases: CVE-2026-43930, GHSA-jpq4-7fmq-q5fj
Ecosystem: Bitnami
Published: 2026-05-14
Source: https://osv.dev/vulnerability/BIT-parse-2026-43930
Type: osv

## Affected
- Bitnami: `parse` — affected >=9.0.0 <9.9.0

## Details
Parse Server is an open source backend that can be deployed to any infrastructure that can run Node.js. Prior to 8.6.76 and 9.9.0, a race condition in the MFA SMS one-time password (OTP) login path allows two concurrent /login requests carrying the same OTP to both succeed and both receive valid session tokens, breaking the single-use property of the OTP. The vulnerability requires the attacker to already possess the victim's password and intercept the active SMS OTP (e.g. via SIM swap, network mirror, or phishing relay) and to race the legitimate login request, so the practical attack surface is narrow. This vulnerability is fixed in 8.6.76 and 9.9.0.

## References
- https://github.com/parse-community/parse-server/pull/10448
- https://github.com/parse-community/parse-server/pull/10449
- https://github.com/parse-community/parse-server/security/advisories/GHSA-jpq4-7fmq-q5fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-43930
