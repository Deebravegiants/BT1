# [H] Missing InResponseTo validation in Samly allows acceptance of unsolicited SAML responses

## Summary
Severity: High
Advisory: EEF-CVE-2026-53425
Aliases: CVE-2026-53425
Ecosystem: Hex
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/EEF-CVE-2026-53425
Type: osv

## Affected
- Hex: `samly` — affected >=0.3.0

## Details
## Summary

Insufficient Verification of Data Authenticity vulnerability in dropbox samly allows an attacker to establish an authenticated session using a SAML response the service provider never requested.

`Samly.SPHandler.validate_authresp/3` in `lib/samly/sp_handler.ex` validates a SAML response for the SP-initiated flow by comparing only the `RelayState` value, the IdP identifier, and the presence of a target URL held in the session. It never compares `SubjectConfirmationData/@InResponseTo` against the ID of the `AuthnRequest` the service provider issued, and that request ID is never persisted, so no comparison is possible. SAML 2.0 Core section 4.1.4.3 requires a service provider to reject a response whose `InResponseTo` does not match a request it made. The underlying `esaml` library checks status, signature, recipient, audience, and staleness, but likewise never inspects `InResponseTo`, so nothing else closes the gap. Exploitation requires a validly signed assertion from the trusted IdP, which an attacker can obtain for their own account, and a `RelayState` matching the victim's session; the assertion signature itself remains intact, so this is not a signature-forgery issue.

This issue affects samly: from 0.3.0 onward.

## References
- https://cna.erlef.org/cves/CVE-2026-53425.html
- https://hex.pm/packages/samly
