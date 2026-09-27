# [H] SimpleSAMLphp HTTP-Artifact TLS validator confusion allows cross-IdP authentication bypass

## Summary
Severity: High
Advisory: GHSA-6929-8p9f-26jx
CVE: CVE-2026-49283
CWE: CWE-295
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-6929-8p9f-26jx
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/saml2` — affected >=6.0.0 <6.2.1
- Packagist: `simplesamlphp/saml2` — affected >=5.0.0 <5.0.6
- Packagist: `simplesamlphp/saml2` — affected >=4.20.0 <4.20.2
- Packagist: `simplesamlphp/saml2-legacy` — affected >=4.20.0 <4.20.2
- Packagist: `simplesamlphp/saml2` — affected >=0 <4.19.3
- Packagist: `simplesamlphp/saml2-legacy` — affected >=0 <4.19.3

## Details
## Summary

SimpleSAMLphp's HTTP-Artifact receive path can treat an unsigned embedded SAML `Response` as cryptographically valid for the wrong IdP.

In the `HTTPArtifact::receive()` flow, the SOAP `ArtifactResponse` receives a TLS-based validator from `SOAPClient::addSSLValidator()`. The embedded SAML `Response` then receives a validator that delegates signature validation to that outer `ArtifactResponse`. Later, the SP validates the embedded `Response` against metadata selected from the embedded response issuer, not necessarily the artifact issuer.

The critical issue is that `SOAPClient::validateSSL()` returns normally when the TLS public key does not match the key currently being validated. `SAML2\Message::validate()` treats any validator call that does not throw an exception as successful. As a result, an `ArtifactResponse` obtained from one IdP can validate an unsigned embedded SAML `Response` that claims to be issued by a different IdP.

In a multi-IdP/federation deployment where a malicious or lower-trust IdP can issue an HTTP-Artifact response to an SP, this can allow the attacker to authenticate to the SP as arbitrary users from a higher-trust victim IdP.

## Impact

A malicious or lower-trust IdP in the same SP/federation trust set can authenticate to the SP as users from another IdP when HTTP-Artifact is used. The attacker can choose assertion attributes, `NameID`, and session data in the forged unsigned assertion.

This is an authentication bypass and identity-provider impersonation issue. In realistic federations, the security boundary between IdPs matters: a compromised or low-assurance IdP should not be able to mint identities for a high-assurance IdP.

## References
- https://github.com/simplesamlphp/saml2/security/advisories/GHSA-6929-8p9f-26jx
- https://github.com/simplesamlphp/saml2
