# [M] @node-oauth/oauth2-server: PKCE code_verifier ABNF not enforced in token exchange allows brute-force redemption of intercepted authorization codes

## Summary
Severity: Medium
Advisory: GHSA-jhm7-29pj-4xvf
CVE: CVE-2026-41213
CWE: CWE-1289, CWE-307
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-jhm7-29pj-4xvf
Type: github-advisory

## Affected
- npm: `@node-oauth/oauth2-server` — affected >=0 <5.3.0

## Details
## Summary

The token exchange path accepts RFC7636-invalid `code_verifier` values (including one-character strings) for `S256` PKCE flows.  
Because short/weak verifiers are accepted and failed verifier attempts do not consume the authorization code, an attacker who intercepts an authorization code can brute-force `code_verifier` guesses online until token issuance succeeds.



### Root cause

1. `lib/pkce/pkce.js` (`getHashForCodeChallenge`) only checks that `verifier` is a non-empty string before hashing for `S256`; it does not enforce RFC7636 ABNF (`43..128` unreserved chars).
2. `lib/grant-types/authorization-code-grant-type.js` compares `hash(code_verifier)` to stored `codeChallenge` without validating verifier format/length.
3. In `AuthorizationCodeGrantType.handle`, authorization code revocation happens **after** verifier validation. Invalid guesses fail before revoke, so the same code can be retried repeatedly.

## Steps to Reproduce

### Setup

- PKCE authorization code exists with:
  - `codeChallengeMethod = "S256"`
  - `codeChallenge = BASE64URL(SHA256("z"))` (verifier is one character, RFC-invalid)
- Attacker has intercepted the authorization code value.

### Reproduction

1. Send repeated token requests with guessed `code_verifier` values:

```http
POST /token HTTP/1.1
Host: oauth.example
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
client_id=client1&
client_secret=s3cret&
code=stolen-auth-code&
redirect_uri=https://client.example/callback&
code_verifier=<guess>
```

2. Observe invalid guesses return `invalid_grant`.
3. Continue guessing (`a`..`z`).
4. When `code_verifier=z`, token issuance succeeds and returns bearer tokens.

### Confirmed PoC output

```text
BRUTE_FORCE_SUCCESS { tries: 26, guess: 'z', status: 200, tokenIssued: true }
```

## Impact

An intercepted authorization code can be redeemed by brute-forcing low-entropy verifiers that the server should have rejected under RFC7636.  
This weakens PKCE’s protection goal and allows token theft when clients generate short/predictable verifiers.

## Recommended Fix

1. Enforce `pkce.codeChallengeMatchesABNF(request.body.code_verifier)` in authorization code token exchange before hashing/comparison.
2. Reject verifier values outside RFC7636 charset/length (`43..128` unreserved).
3. Invalidate authorization codes on failed verifier attempts (or add strict retry limits) to prevent online guessing.

## References
- https://github.com/node-oauth/node-oauth2-server/security/advisories/GHSA-jhm7-29pj-4xvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-41213
- https://github.com/node-oauth/node-oauth2-server
