# [M] Making all attributes on a content-type public without noticing it

## Summary
Severity: Medium
Advisory: GHSA-chmr-rg2f-9jmf
CVE: CVE-2023-34093
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-chmr-rg2f-9jmf
Type: github-advisory

## Affected
- npm: `@strapi/strapi` — affected >=0 <4.10.8
- npm: `@strapi/utils` — affected >=0 <4.10.8
- npm: `@strapi/database` — affected >=0 <4.10.8

## Details
### Summary
Anyone (Strapi developers, users, plugins) can make every attribute of a Content-Type public without knowing it.

### Details
When dealing with content-types inside a Strapi instance, we can extend those using the appropriate container:
```javascript
strapi.container.get('content-types').extend(contentTypeUID, (contentType) => newContentType);
```
The vulnerability only affects the handling of content types by Strapi, not the actual content types themselves. Users can use plugins or modify their own content types without realizing that the `privateAttributes` getter is being removed, which can result in any attribute becoming public. This can lead to sensitive information being exposed or the entire system being taken control of by an attacker(having access to password hashes).

### PoC
Extend any content type on runtime (like in the bootstrap functions) and do a copy of the content-type object.
```javascript
strapi.container.get('content-types').extend(contentTypeUID, (contentType) => {
  const newCT = { ... contentType, attributes: { ...contentType.attributes, newAttr: {} } };
  return newCT;
});
```
This will have as effect to remove the getter and as we rely on it in sanitization, every attributes will be considered as public.

### Impact
Everyone can be impacted. Depending on how people are using/extending content-types. If the users are mutating the content-type, they will not be affected.

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-chmr-rg2f-9jmf
- https://nvd.nist.gov/vuln/detail/CVE-2023-34093
- https://github.com/strapi/strapi/commit/2fa8f30371bfd1db44c15e5747860ee5789096de
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v4.10.8
