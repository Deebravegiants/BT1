# [H] Missing one-time-use enforcement in Samly allows replay of SAML bearer assertions

## Summary
Severity: High
Advisory: EEF-CVE-2026-53424
Aliases: CVE-2026-53424
Ecosystem: Hex
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/EEF-CVE-2026-53424
Type: osv

## Affected
- Hex: `samly` — affected >=0.3.0

## Details
## Summary

Authentication Bypass by Capture-replay vulnerability in dropbox samly allows an attacker to authenticate as the subject of a captured SAML assertion by resubmitting it.

`Samly.Helper.decode_idp_auth_resp/3` in `lib/samly/helper.ex` calls `esaml_sp:validate_assertion/2`, whose default duplicate detector is a no-op. The `/3` arity accepting a `DuplicateFun` exists in `esaml` and implements the check, but Samly never calls it and offers no configuration to supply one, so the SAML 2.0 Web Browser SSO Profile requirement that a bearer assertion be used once is unenforced. An attacker holding a valid `SAMLResponse` obtained from the network, from browser history, or from logs can submit the identical bytes repeatedly until the assertion's `NotOnOrAfter` passes, each time establishing a session as the assertion's subject.

This issue affects samly: from 0.3.0 onward.

## References
- https://cna.erlef.org/cves/CVE-2026-53424.html
- https://hex.pm/packages/samly
