# [M] Guardian.revoke/3 acts on unverified token claims, allowing forged-token session revocation

## Summary
Severity: Medium
Advisory: CVE-2026-55735
Aliases: EEF-CVE-2026-55735, GHSA-7975-hp3r-5qhv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-55735
Type: osv

## Details
Improper Verification of Cryptographic Signature in ueberauth guardian allows an unauthenticated attacker to revoke a victim's session with a forged token.

Guardian.revoke/3 in lib/guardian.ex decodes the supplied token with peek/1, which performs no signature verification (it only base64-decodes the JWT header and payload). The resulting unverified claims are forwarded directly to the configured token module's revoke callback and the implementation's on_revoke callback, a state-mutating sink. The sibling operations refresh/2 and exchange/4 both call decode_and_verify first, so the signature is checked before anything acts on the claims; revoke/3 is the only state-mutating path that acts on claims without verifying the signature.

An attacker who knows or guesses a victim's identifying claim values (jti, sub) can forge a JWT carrying those claims, sign it with an arbitrary key, and submit it to any endpoint that funnels a caller-supplied token into Guardian.revoke/3 (the standard logout / session-revocation pattern). When the token module mutates state keyed by the claims (whitelist deletion or blacklist insertion, for example a GuardianDb-style store), the victim's legitimate session is evicted. This is an unauthenticated session-revocation denial of service; the attacker never needs the signing secret.

This issue affects guardian: from 1.0.0 before 2.4.1.

## References
- https://cna.erlef.org/cves/CVE-2026-55735.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-55735
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55735.json
- https://github.com/ueberauth/guardian/security/advisories/GHSA-7975-hp3r-5qhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-55735
- https://github.com/ueberauth/guardian/commit/2bd7a8c29770d423d855c0a4965caa6c3e486901
- https://github.com/ueberauth/guardian
