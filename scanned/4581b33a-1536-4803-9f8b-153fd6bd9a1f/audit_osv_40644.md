# [M] Cap-go < v12.128.2 Account Takeover via Unauthenticated Email Change Mechanism

## Summary
Severity: Medium
Advisory: CVE-2026-53981
Aliases: GHSA-w56g-jv78-hf79
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-53981
Type: osv

## Details
Cap-go prior to 12.128.2 contains an account takeover vulnerability in its email change mechanism that allows an attacker with temporary authenticated session access to change the registered email address without re-authentication such as password or MFA verification. Attackers can redirect verification to an attacker-controlled email address and subsequently perform a password reset to permanently take over the victim's account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53981.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-w56g-jv78-hf79
- https://nvd.nist.gov/vuln/detail/CVE-2026-53981
- https://www.vulncheck.com/advisories/cap-go-account-takeover-via-unauthenticated-email-change-mechanism
- https://github.com/Cap-go/capgo/commit/6685e5f11adef257bf3d085e481f4d8ebcec602e
