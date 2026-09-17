# [H] The SimpleSAMLphp SAML2 library incorrectly verifies signatures for HTTP-Redirect binding

## Summary
Severity: High
Advisory: GHSA-46r4-f8gj-xg56
CVE: CVE-2025-27773
CWE: CWE-347
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-46r4-f8gj-xg56
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/saml2` — affected >=0 <4.17.0
- Packagist: `simplesamlphp/saml2` — affected >=5.0.0-alpha.1 <5.0.0-alpha.20
- Packagist: `simplesamlphp/saml2-legacy` — affected >=0 <4.17.0

## Details
### Summary
There's a signature confusion attack in the HTTPRedirect binding. An attacker with any signed SAMLResponse via the HTTP-Redirect binding can cause the application to accept an unsigned message.

I believe that it exists for v4 only. I have not yet developed a PoC.

V5 is well designed and instead builds the signed query from the same message that will be consumed.
### Details

#### What is verified
The data['SignedQuery'] is the string that will be verified by the public key. 

It is defined here:
https://github.com/simplesamlphp/saml2/blob/9545abd0d9d48388f2fa00469c5c1e0294f0303e/src/SAML2/HTTPRedirect.php#L178-L217

THe code will iterate through each parameter name. Notably, sigQuery is overridden each time when processing, making the last of SAMLRequest/SAMLResponse used for sigQuery.

For example, given:

SAMLRequest=a&SAMLResponse=idpsigned

SAMLResponse=idpsigned will be set as sigQuery, then later verified


#### What is actually processed

Processing uses SAMLRequest parameter value first, (if it exists) then SAMLResponse:

https://github.com/simplesamlphp/saml2/blob/9545abd0d9d48388f2fa00469c5c1e0294f0303e/src/SAML2/HTTPRedirect.php#L104-L113

Given this, the contents that are processed might not be the same as the data that is actually verified.


### Exploiting
Suppose an attacker has a signed HTTP Redirect binding from IdP, say a signed logout response. :

SAMLResponse=idpsigned&RelayState=...&SigAlg=...&Signature


Then an attacker can append SAMLRequest in front:

`SAMLRequest=unverifieddata&SAMLResponse=idpsigned&RelayState=...&SigAlg=...&Signature=..`

SimpleSAMLPhp will only verify the SAMLResponse, but will actually use the SAMLRequest contents. The impact here is increased because there's no checks that SAMLRequest actually contains a Request, it could instead contain an Response, which allows the attacker to effectively impersonate any user within the SP.


### IdPs

Microsoft Azure AD/Entra (and likely ADFS) signs the LogoutResponse via this SimpleSign format in HTTP Redirect binding. If an attacker logs out of Entra, they will be able to extract a valid Signature.

Attached is an HTTP Request when an I initiated a SLO request from the service provider to the IdP (entra). Then IdP POSTed this SAMLResponse with HTTP Redirect binding signature, via the user browser to the SP. It should be possible to carry out the described attack with this.

```
https://webhook.site/c6038292-6ef5-46ac-973d-d7c25520ec48/logout?SAMLResponse=fVJNa%2bMwEP0rRndZtmw5tnAMy%2fYSaC9N6aGXIsmjVMTRGI9M%2bvObdeihsPQ4w7x5HzM9mcs060c84ZqegWaMBNnhYc%2fejS1UW1TAnVU7XldK8s7JkcvOd60Db3zTsewVFgoY90zmBcsORCscIiUT061VyJqXJS%2fbl7LRUmrZ5mXdvLHsASiFaNKG%2fEhpJi3EFewH4jmnkEC4pqha2UnegFe8bozj3a4a%2bbhzUilZgKtbMW2yb7TxW%2foL7lkM9hTC2XnEOPvZXjDECb2N1lh7mvBsp%2bnsErDs8zJF0lsEe7YuUaOhQDqaC5BOTh%2f%2fPD3qmzE9L5jQ4cSGfrO43KG%2fgwwRLP8ssuHbIiXKryGOeKU8QhLSVN7WteejV8Bru%2bt4WynFbwE3bdVV5ahG0Ys759Dfj3VMJq30s%2fqLI2SvZlrhd020Tevj6hwQMTH04udS8b%2bHGL4A&Signature=Z%2f7gIPv7Gkgvqtwo0bzgXyum9IjHMfP0zTYuNbl%2fBUGlQ%2fU%2bbOZGZJ6Rk9wLUyvNQ5XlZRxZrfESNA%2bn0CVyIedsg9GxQKTi7VqPTJFJqEIP1BZaEpYYP3%2f6sFfLxfTMKecJoQdxnDE5Malte1hMj2UujWnLXOnp0CgO%2f%2fU2K52SoGckIzNDRB%2fJ6%2fysTn%2bDjBrmgdro%2fgdTyby9%2f3vm8dzY8pUkRCgMjlimShrZxr5U33wQvwPLIXlDgActr91RUtWKE0k8sy%2brshrK9DKLPo8AdTLk7NYhjSWdF7OG7uqgEeEo470tacqQuA09E0qDh8CWS%2bycLJijiGYWVyQa4Q%3d%3d&SigAlg=http%3a%2f%2fwww.w3.org%2f2001%2f04%2fxmldsig-more%23rsa-sha256
```

## References
- https://github.com/simplesamlphp/saml2/security/advisories/GHSA-46r4-f8gj-xg56
- https://nvd.nist.gov/vuln/detail/CVE-2025-27773
- https://github.com/simplesamlphp/saml2/commit/7867d6099dc7f31bed1ea10e5bea159c5623d2a0
- https://github.com/simplesamlphp/saml2
- https://github.com/simplesamlphp/saml2/blob/9545abd0d9d48388f2fa00469c5c1e0294f0303e/src/SAML2/HTTPRedirect.php#L104-L113
- https://github.com/simplesamlphp/saml2/blob/9545abd0d9d48388f2fa00469c5c1e0294f0303e/src/SAML2/HTTPRedirect.php#L178-L217
- https://lists.debian.org/debian-lts-announce/2025/05/msg00013.html
