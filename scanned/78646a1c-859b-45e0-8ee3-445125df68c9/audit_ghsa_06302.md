# [H] node-opcua missing nonce verification in UserNameIdentityToken authentication

## Summary
Severity: High
Advisory: GHSA-mq36-523m-x7vv
CVE: CVE-2026-54155
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-mq36-523m-x7vv
Type: github-advisory

## Affected
- npm: `node-opcua` — affected >=0

## Details
**Summary**
A missing nonce verification in the UserNameIdentityToken authentication handler allows an unauthenticated remote attacker to forge a password token that extracts as an empty string, and to replay captured authentication tokens across sessions.

**Affected versions:** <= 2.165.0
**Tested version:** 2.165.0
**CVSS Score:** 8.1 (High)
**CVSS Vector:** CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L
**CWE:** CWE-347 Improper Verification of Cryptographic Signature

---

**Root Cause**

In `packages/node-opcua-server/source/opcua_server.ts` at line 1886-1887, after RSA-OAEP decrypting the UserNameIdentityToken password blob, the server reads a 4-byte little-endian length field and extracts `buff[4 : 4+length]` as the password. It never verifies that the trailing bytes equal `session.nonce`.

This has two consequences:

1. **Forged empty password:** An attacker who retrieves the server's public key via an unauthenticated `GetEndpoints` call can craft a token where the 4-byte length field equals `serverNonce.length` (32). The server computes `length = 32 - 32 = 0` and calls `isValidUser(username, "")`. Any account that accepts an empty password is compromised.

2. **Unconditional replay attack:** Because nonce binding is structurally absent, any captured UserNameIdentityToken ciphertext can be replayed in a different session unconditionally.

The impact is compounded by a second issue: when the channel uses `SecurityMode=None`, `verifyClientSignature` returns `true` unconditionally (security_policy.ts:697-700), bypassing the channel-level signature check entirely.

---

**Proof of Concept (logic, no exploit code)**

```
1. GetEndpoints (unauthenticated) → retrieve server public key and RSA token policy
2. OpenSecureChannel (SecurityMode=None)
3. CreateSession
4. Craft plaintext: [0x20, 0x00, 0x00, 0x00]  (readUInt32LE = 32 = serverNonce.length)
5. RSA-OAEP encrypt with server public key → 256-byte ciphertext
6. ActivateSession with crafted UserNameIdentityToken
7. Server decrypts → length = 32 - 32 = 0 → password = ""
8. isValidUser(username, "") is called
```

Dynamically confirmed: decryption produces `password = ""` with no error and no nonce verification.

---

**Suggested Fix**

After decrypting the password blob, verify that `buff.slice(4 + passwordLength)` equals `session.nonce` before extracting the password. Reject the token if verification fails.

---

I am following a 90-day responsible disclosure policy. I am happy to provide additional technical details under embargo. Please confirm receipt at your earliest convenience.

Reporter: Stanley Tobias
Discovery date: 2026-03-23

## References
- https://github.com/node-opcua/node-opcua/security/advisories/GHSA-mq36-523m-x7vv
- https://github.com/node-opcua/node-opcua
