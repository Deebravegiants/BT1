# [H] Omni has a TOCTOU race condition that allows multiple concurrent uses of a single-use SAML session token

## Summary
Severity: High
Advisory: GHSA-5x9f-6vg5-qg4m
CVE: CVE-2026-45720
CWE: CWE-294, CWE-367
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-5x9f-6vg5-qg4m
Type: github-advisory

## Affected
- Go: `github.com/siderolabs/omni` — affected >=0 <1.6.6
- Go: `github.com/siderolabs/omni` — affected >=1.7.0 <1.7.3

## Details
## Summary

`SAML.getSession` (`internal/pkg/auth/interceptor/saml.go`) checks the `Used` flag on a `SAMLAssertion` resource and then marks it used in two separate state operations. Because the check and the update are not atomic, concurrent requests carrying the same `saml-session` token can both observe `Used == false`, both pass validation, and both return a successful authentication context. An attacker who obtains a valid `saml-session` token can exploit this window to authenticate as the token's owner multiple times, defeating the one-time-use guarantee.

## Severity

- **Attack Vector:** Local: the attacker needs to either be able to intercept the local, unencrypted traffic or needs access to user's browser.
- **Attack Complexity:** High: the attacker must first obtain a valid `saml-session` token belonging to the victim (requires a separate interception step; the token is ephemeral and single-use by design).
- **Privileges Required:** None: no Omni account is required to carry out the race once the session token is in hand.
- **User Interaction:** Required: the victim must initiate a SAML authentication flow to produce the session token that the attacker intercepts.
- **Scope:** Unchanged: the impact stays within Omni's authorization boundary.
- **Confidentiality Impact:** High: successful exploitation authenticates the attacker as the victim's email identity, granting read access to any resource accessible to that identity.
- **Integrity Impact:** High: the attacker can confirm one or more public keys under the victim's identity (via `ConfirmPublicKey`), establishing persistent access credentials tied to the victim's account.
- **Availability Impact:** High: if the attacker can successfully perform the attack and if the victim is a privileged Omni user, e.g., an Omni Operator or Admin, they can take Omni down.

## Impact

- **Session replay**: A stolen `saml-session` token can be used more than once, defeating its single-use guarantee.
- **Multiple public key confirmations**: An attacker who steals the session can confirm N attacker-controlled public keys under the victim's identity in a single stolen session window, creating N persistent long-lived API credentials tied to the victim's account.
- **Authentication as victim**: Any gRPC endpoint gated by the SAML interceptor can be reached as the victim's email identity during the race window.
- **Audit log pollution**: Each raced call generates an audit entry attributed to the victim's email, obscuring the attacker's actions.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/siderolabs/omni/security/advisories/GHSA-5x9f-6vg5-qg4m
- https://github.com/siderolabs/omni
- https://github.com/siderolabs/omni/releases/tag/v1.6.6
- https://github.com/siderolabs/omni/releases/tag/v1.7.3
