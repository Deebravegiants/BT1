# [H] Missing ID token claim validation in ueberauth_apple allows account takeover

## Summary
Severity: High
Advisory: CVE-2026-55954
Aliases: EEF-CVE-2026-55954, GHSA-pxx8-68pc-p9mr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-55954
Type: osv

## Details
Authentication Bypass by Spoofing vulnerability in ueberauth ueberauth_apple allows account takeover via unvalidated ID token claims.

The Ueberauth.Strategy.Apple.Token.payload/2 function verifies the JWT signature of the callback id_token against Apple's JWKS but does not validate any registered claims. The iss, aud, exp, and iat claims are read from the token and passed on to Ueberauth.Strategy.Apple.handle_callback!/1, which derives the logged-in user's uid and email directly from the unvalidated sub claim.

An attacker who obtains any Apple-signed ID token bearing the victim's sub (via a captured expired token, or via an ID token issued to a sibling client in the same Apple developer team) can replay it against the vulnerable callback and be authenticated as the victim. The absent exp check makes stolen tokens usable indefinitely, and the absent aud check enables cross-application account takeover across clients that share an Apple developer team.

This issue affects ueberauth_apple: from 0.1.0 before 0.6.2.

## References
- https://cna.erlef.org/cves/CVE-2026-55954.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-55954
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55954.json
- https://github.com/ueberauth/ueberauth_apple/security/advisories/GHSA-pxx8-68pc-p9mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-55954
- https://github.com/ueberauth/ueberauth_apple/commit/01e2d9c9b3134e1b78633ad82d136d5ff4a61f28
- https://github.com/ueberauth/ueberauth_apple
