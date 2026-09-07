# [C] OpenBao lacks user confirmation for OIDC direct callback mode

## Summary
Severity: Critical
Advisory: GHSA-7q7g-x6vg-xpc3
CVE: CVE-2026-33757
CWE: CWE-384
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-7q7g-x6vg-xpc3
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20260325142553-e32103951925

## Details
### Impact

OpenBao does not prompt for user confirmation when logging in via JWT/OIDC and a role with `callback_mode` set to `direct`.

This allows an attacker to start an authentication request and perform "remote phishing" by having the victim visit the URL and automatically log-in to the session of the attacker. Despite being based on the authorization code flow, the  `direct` mode calls back directly to the API and allows an attacker to poll for an OpenBao token until it is issued.

### Patches
Version 2.5.2 includes an additional confirmation screen for `direct` type logins that requires manual user interaction in order to finish the authentication.

### Workarounds
This issue can be worked around either by removing any roles with `callback_mode=direct` or enforcing confirmation for every session on the token issuer side for the Client ID used by OpenBao.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-7q7g-x6vg-xpc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33757
- https://github.com/openbao/openbao/commit/e32103951925723e9787e33886ab6b6ec20f4964
- https://datatracker.ietf.org/doc/html/rfc8628#section-5.4
- https://github.com/openbao/openbao
