# [M] SimpleSAMLphp Reflected Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vpr3-cw3h-prw8
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-vpr3-cw3h-prw8
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=1.12.0 <1.17.3

## Details
### Background
SimpleSAMLphp uses metadata to determine how to interact with other SAML entities. This metadata includes what’s called endpoints, which are URLs belonging to that entity where SAML messages can be sent. These URLs are used directly by SimpleSAMLphp when a message is sent, either via an HTTP redirection or by automatically posting a form to them.

### Description
When sending a SAML message to another entity, SimpleSAMLphp will use the URL of the appropriate endpoint to redirect the user’s browser to it, or craft a form that will be automatically posted to it, depending on the SAML binding used. The URL that’s target of the message is fetched from the stored metadata for the given entity, and that metadata is trusted as correct.

However, if that metadata has been altered by a malicious party (either an attacker or a rogue administrator) to substitute the URLs of the endpoints with javascript code, SimpleSAMLphp was blindly using them without any validation, trusting the contents of the metadata. This would lead to a reflected XSS where the javascript code is sent inline to the web browser, and if SimpleSAMLphp is not using a strict Content Security Policy to forbid inline javascript (which is the case of the default user interface), then the code will be executed in the end user’s browser.

### Affected versions
All SimpleSAMLphp versions are affected, up to 1.17.2.

### Impact
If metadata is consumed for a rogue entity that includes javascript code in the corresponding endpoints, this javascript code might be run by users trying to access this entity.

Even though it’s unlikely that an administrator would add metadata for an entity that contains such endpoints inadvertently, if metadata is consumed automatically (e.g. using metarefresh) it would be easier to have an scenario like the one described here if a SAML entity is compromised and its metadata modified.

The severity is assessed as medium given the difficulty to exploit the issue.

## References
- https://github.com/simplesamlphp/simplesamlphp/commit/ce2294e092b3be7db2fc4e18e774b791d4564ff3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/2019-07-10.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://simplesamlphp.org/security/201907-01
