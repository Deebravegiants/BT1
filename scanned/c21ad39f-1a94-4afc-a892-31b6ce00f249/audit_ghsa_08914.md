# [C] Casdoor SAML callback handler accepts any well-formed SAMLResponse sent to /api/acs without verifying that it corresponds to an AuthnRequest

## Summary
Severity: Critical
Advisory: GHSA-mfvp-7p3v-x9mh
CVE: CVE-2026-9098
CWE: CWE-488
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-mfvp-7p3v-x9mh
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
In Casdoor versions 2.362.0 and earlier, the SAML callback handler in controllers/auth.go accepts any well-formed SAMLResponse sent to /api/acs without verifying that it corresponds to an AuthnRequest previously issued by Casdoor. Additionally, if an administrator disables or deletes an IdP (Identity Provider) after a SAML flow has started, the handler still processes the response using the provider snapshot loaded at the start of the request. As a result, an attacker controlling a registered upstream IdP can send unsolicited SAML responses, or replay a legitimately captured response in a different session or after the original flow has ended. In both cases, Casdoor accepts the response and issues a session, enabling persistent unauthorized access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9098
- https://github.com/casdoor/casdoor
- https://kb.cert.org/vuls/id/780781
