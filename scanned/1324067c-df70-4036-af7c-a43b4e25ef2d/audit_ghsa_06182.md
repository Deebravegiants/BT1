# [H] Open WebUI: Account takeover via OAuth token exchange accepting tokens issued to any client

## Summary
Severity: High
Advisory: GHSA-rq84-p6rr-vf89
CVE: CVE-2026-70482
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-rq84-p6rr-vf89
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.8.0 <0.11.0

## Details
## Summary

The OAuth token exchange endpoint accepts a raw provider access token and validates it by calling the provider's userinfo endpoint. A userinfo endpoint reports only that a token is valid, never which OAuth client it was issued to, and the endpoint performed no audience or client check of its own. Anyone holding an access token minted for any client registered with the same provider could exchange it for an Open WebUI session as that token's user, including applications the operator does not control and has never authorised.

## Preconditions

- `ENABLE_OAUTH_TOKEN_EXCHANGE=True`. Disabled by default, so a stock deployment is not affected.
- The victim already has an Open WebUI account. The endpoint does not create users.
- The attacker can obtain a provider access token for the victim, typically by having them sign in to an unrelated OAuth application on the same provider. On public providers, registering that application is self-service.
- The subject identifier the attacker's client observes matches the one stored on the victim's account. Google, GitHub, Okta and self-hosted OIDC servers in default configuration issue a subject that is stable across all clients and are directly affected. Microsoft Entra ID issues per-application subjects, so the match fails there unless `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` is enabled or `OAUTH_SUB_CLAIM` points at a globally stable claim such as `oid`.
- `OAUTH_ALLOWED_DOMAINS` is enforced on this endpoint but does not constrain the attack, because the impersonated user is a legitimate member of an allowed domain.

## Impact

Full account takeover of any user whose provider access token the attacker can obtain. The endpoint applies no role gating, so the issued session carries the target account's role, and a targeted administrator yields an administrator session. The victim never interacts with Open WebUI and has no opportunity to notice.

The standard OAuth callback is not affected. It obtains its token through an authorization-code exchange authenticated with the client secret, so the token is inherently bound to Open WebUI's own client, and the ID token's audience is validated.

## Fix

Fixed in 0.11.0. The endpoint now resolves which OAuth client a presented token was issued to through RFC 7662 token introspection, and rejects tokens minted for any client not named in `OAUTH_TOKEN_EXCHANGE_TRUSTED_CLIENT_IDS`. Only the introspected `client_id` is honoured; the `aud` field is ignored, because it names intended resource servers rather than the issuing client and several providers let any client place another client's identifier there.

**Upgrading alone is not sufficient.** The check is opt-in: with `OAUTH_TOKEN_EXCHANGE_TRUSTED_CLIENT_IDS` unset the endpoint behaves as it did before, so any deployment running with `ENABLE_OAUTH_TOKEN_EXCHANGE=True` must also set that list. It is a deploy-time environment variable and cannot be changed from the admin interface, so a compromised administrator session cannot widen the trust boundary at runtime.

Providers that do not implement RFC 7662 introspection, including Google, Microsoft Entra ID, GitHub and Feishu, cannot be restricted this way at all. **On those, token exchange has no safe configuration and should be left disabled.**

## Root cause

- `backend/open_webui/routers/auths.py`, `token_exchange` (`POST /api/v1/auths/oauth/{provider}/token/exchange`)

Token exchange skips the authorization-code step entirely and trusts a token supplied by the caller. The only validation performed was a userinfo lookup, which answers whether a token is valid rather than who issued it, so the endpoint had no way to distinguish a token minted for Open WebUI from one minted for an unrelated application.

## Proof of concept

Reproduced against a mock OIDC provider serving two tokens for the same end user, minted for two different clients, with `OAUTH_ALLOWED_DOMAINS=corp.example` actively enforced.

| Case | Token | Result |
| --- | --- | --- |
| Control | not recognised by the provider | 400 rejected |
| Outsider's own account, non-allowed domain | minted for `attacker-evil-app` | 403 blocked by domain allowlist |
| Victim's account, foreign client | minted for `attacker-evil-app` | 200, session issued for `victim@corp.example` |

The issued session token was confirmed usable: `GET /api/v1/auths/` returned 200 authenticated as the victim. The provider log recorded the token as minted for `client_id='attacker-evil-app'`, while Open WebUI's own client is `openwebui-client-id`.

## Credits

Reported by @Classic298.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-rq84-p6rr-vf89
- https://github.com/open-webui/open-webui/commit/b190dcf3caa00dc8b7b9c7312828298d9143f60d
- https://github.com/open-webui/open-webui/commit/c4332be71e6e9c314e8a13b9d2819a6932561630
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0
