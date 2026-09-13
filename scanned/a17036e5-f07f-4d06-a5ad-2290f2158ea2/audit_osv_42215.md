# [H] Purpose-limited JWT accepted as full bearer authentication in AshAuthentication

## Summary
Severity: High
Advisory: CVE-2026-65633
Aliases: EEF-CVE-2026-65633, GHSA-6vcj-3h59-rrc3
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-65633
Type: osv

## Details
Improper Authentication vulnerability in team-alembic AshAuthentication allows purpose-limited JWTs to be replayed as full bearer API credentials when a resource uses stateless bearer-token verification.

The bearer-token authentication helper AshAuthentication.Plug.Helpers.retrieve_from_bearer/3 verifies an Authorization: Bearer JWT's signature and rejects tokens containing an act claim, but performs no check that the token's purpose claim equals user at the bearer boundary. When the resource is configured with require_token_presence_for_authentication?: false (the DSL default), the follow-on validate_token/3 helper returns {:ok, nil} without consulting the token resource, so no downstream check on purpose takes place either. As a result, any valid, non-expired JWT the library itself issued for a narrow, single-purpose flow (most notably the purpose: sign_in token that WebAuthn always emits during sign-in, and that the Password strategy emits when sign-in tokens are enabled) is accepted directly as a general-purpose bearer credential and resolves to a full current_user assignment.

This bypasses the library's intended token-exchange contract, in which the sign_in token is meant to be presented exactly once to a preparation that validates the purpose claim and immediately revokes the token. The first use of a still-valid sign-in token presented directly in the Authorization header succeeds because the stateless bearer path never scopes it to purpose == "user".

An attacker who obtains a not-yet-exchanged sign-in token for a target subject (for example via log or referrer leakage, an intercepted magic-link delivery channel, or a partially compromised intermediary) can present it as a bearer token and be authenticated as that subject, fully bypassing the intended one-time-use and revocation semantics. Exploitation additionally requires that the host application wire up retrieve_from_bearer/3 on a reachable route and uses either WebAuthn (sign-in tokens are always issued) or the Password strategy with sign_in_tokens_enabled?: true. Resources configured with require_token_presence_for_authentication?: true (including applications scaffolded by the Igniter installer since v4.5.0) and the session-based path (authenticate_resource_from_session/4) enforce purpose == "user" against the stored token record and are not affected.

This issue affects ash_authentication: from 3.10.5 before 4.14.2 and from 5.0.0-rc.0 before 5.0.0-rc.13.

## References
- https://cna.erlef.org/cves/CVE-2026-65633.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-65633
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65633.json
- https://github.com/team-alembic/ash_authentication/security/advisories/GHSA-6vcj-3h59-rrc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-65633
- https://github.com/team-alembic/ash_authentication/commit/124eddd1bbeb40289c3fe8831ac10677a19fcf09
- https://github.com/team-alembic/ash_authentication/commit/8cf8b2d4426172be0900a3505e9491800b951750
- https://github.com/team-alembic/ash_authentication
