# [C] Gitea Remember-Me Token Theft Not Invalidating Attacker Session

## Summary
Severity: Critical
Advisory: GHSA-rgv6-xp99-6mgj
CVE: CVE-2026-56750
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-rgv6-xp99-6mgj
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
The vulnerability is in the Remember-Me (gitea_incredible) token validation logic, specifically when handling a compromised token (hash mismatch).

The vulnerable function is this one:

https://github.com/go-gitea/gitea/blob/689ace1ce28fd74244b8aa335d9928cdbf6b22f9/services/auth/auth_token.go#L33-L64

### Affected Endpoint
POST `/user/login` (and any endpoint triggering `autoSignIn` via the Remember-Me cookie).

### Description
Gitea implements Remember-Me cookies using a split token design (ID:Hash), [citing the Paragonie secure remember-me guide](https://github.com/go-gitea/gitea/blob/689ace1ce28fd74244b8aa335d9928cdbf6b22f9/services/auth/auth_token.go#L21). When a token is used, its Hash is rotated, but the ID remains the same.

If an attacker steals a user's Remember-Me token and uses it to authenticate, the attacker is issued a new rotated token (same ID, new Hash). When the legitimate user later attempts to use their original token, Gitea correctly detects a hash mismatch for the given ID.

According to the referenced Paragonie specification, this indicates a compromised token, and ALL active remember-me sessions for that user MUST be invalidated. However, Gitea's `CheckAuthToken` function simply returns `ErrAuthTokenInvalidHash`. The calling code (`autoSignIn`) catches this error and deletes the victim's local cookie via `ctx.DeleteSiteCookie`, but fails to delete the compromised token from the database.

As a result, the attacker's active session is never invalidated, and the attacker maintains persistent, indefinite access to the victim's account, entirely defeating the purpose of the split-token security design.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-rgv6-xp99-6mgj
- https://github.com/go-gitea/gitea/pull/38406
- https://github.com/go-gitea/gitea/pull/38426
- https://github.com/go-gitea/gitea/commit/de4b8277e9cb576f2315fb03b5ab6478b42a1d31
- https://github.com/go-gitea/gitea/commit/f69e15afe7496cc62e96dab244629c69eb31a7bf
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
