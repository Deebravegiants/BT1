# [M] authentik: WS-Federation wreply origin bypass can exfiltrate signed login responses to attacker-controlled endpoints

## Summary
Severity: Medium
Advisory: BIT-authentik-2026-41569
Aliases: CVE-2026-41569, GHSA-995q-72cw-cfw3
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-authentik-2026-41569
Type: osv

## Affected
- Bitnami: `authentik` — affected >=0 <2026.2.3

## Details
authentik is an open-source identity provider. Prior to version 2026.2.3, the WS-Federation provider validates the user-supplied wreply parameter using a raw string prefix check rather than proper URL parsing. An attacker who can craft a login link can supply a wreply value on a different origin that passes the check (e.g. https://portal.example.com.evil.tld/), causing the victim's browser to POST the signed WS-Federation login response to attacker-controlled infrastructure. This issue has been patched in version 2026.2.3.

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-995q-72cw-cfw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41569
