# [H] Unsigned SAML LogoutRequest Acceptance in gosaml2

## Summary
Severity: High
Advisory: GHSA-pcgw-qcv5-h8ch
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-pcgw-qcv5-h8ch
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/gosaml2` — affected >=0 <0.11.0

## Details
## Summary

The `ValidateEncodedLogoutRequestPOST` function in gosaml2 accepts completely unsigned SAML `LogoutRequest` messages even when `SkipSignatureValidation` is set to `false`. When `validateElementSignature` returns `dsig.ErrMissingSignature`, the code in `decode_logout_request.go:60-62` silently falls through to process the unverified XML element instead of rejecting it. An attacker who can reach the SP's Single Logout endpoint can forge a `LogoutRequest` for any user, terminating their session without possessing the IdP's signing key.

## Affected Version

- **Library**: `github.com/russellhaering/gosaml2`
- **Version**: All versions up to and including the latest commit on `main` (as of 2026-03-16)
- **File**: `decode_logout_request.go`, lines 58-69

## Vulnerable Code

```go
// decode_logout_request.go:57-69
var requestSignatureValidated bool
if !sp.SkipSignatureValidation {
    el, err = sp.validateElementSignature(el)
    if err == dsig.ErrMissingSignature {
        // Unfortunately we just blew away our Response
        el = doc.Root()                    // <-- BUG: falls through with unsigned element
    } else if err != nil {
        return nil, err
    } else if el == nil {
        return nil, fmt.Errorf("missing transformed logout request")
    } else {
        requestSignatureValidated = true
    }
}
```

When `ErrMissingSignature` is returned, the code resets `el` to the raw document root and continues. The `requestSignatureValidated` variable remains `false`, but no error is returned. The unsigned `LogoutRequest` is unmarshalled and passed to `ValidateDecodedLogoutRequest`, which performs attribute/issuer checks but does **not** verify that a signature was present.

## Attack Details

| Property | Value |
|---|---|
| **Attack vector** | Network (HTTP POST to SLO endpoint) |
| **Authentication required** | None |
| **Payload size** | ~450 bytes (unsigned XML) |
| **User interaction** | None |
| **Complexity** | Low -- only requires knowledge of the SP's SLO URL and IdP issuer |
| **CVSS estimate** | 7.5 (High) -- Network/Low/None/None, Availability impact |

## Impact

- **Arbitrary session termination**: An attacker can force-logout any user by forging a `LogoutRequest` with the victim's `NameID`. This is a targeted denial-of-service.
- **Business disruption**: Critical users (executives, admins, operators) can be repeatedly logged out, disrupting access to the application during incidents or time-sensitive operations.
- **Security control bypass**: If session termination triggers downstream effects (e.g., revoking tokens, clearing caches), an attacker can weaponize this to force re-authentication flows and potentially intercept them.
- **No cryptographic material needed**: The attacker does not need the IdP's private key. The forged request contains zero cryptographic elements.

## Suggested Fix

When `ErrMissingSignature` is returned and `SkipSignatureValidation` is `false`, the function should return an error instead of falling through:

```go
// decode_logout_request.go -- fixed version
var requestSignatureValidated bool
if !sp.SkipSignatureValidation {
    el, err = sp.validateElementSignature(el)
    if err == dsig.ErrMissingSignature {
        // FIXED: reject unsigned requests when signature validation is required
        return nil, fmt.Errorf("logout request is not signed: %w", dsig.ErrMissingSignature)
    } else if err != nil {
        return nil, err
    } else if el == nil {
        return nil, fmt.Errorf("missing transformed logout request")
    } else {
        requestSignatureValidated = true
    }
}
```

This ensures that unsigned `LogoutRequest` messages are rejected when `SkipSignatureValidation` is `false`, matching the behavior that operators expect when they configure signature enforcement.

Attached lab 
[f1_unsigned_logout.zip](https://github.com/user-attachments/files/26038319/f1_unsigned_logout.zip)

## References
- https://github.com/russellhaering/gosaml2/security/advisories/GHSA-pcgw-qcv5-h8ch
- https://github.com/russellhaering/gosaml2
