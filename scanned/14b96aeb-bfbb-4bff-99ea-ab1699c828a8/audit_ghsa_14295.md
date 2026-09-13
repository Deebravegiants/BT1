# [M] Bypass of CSRF protection in the presence of predictable userInfo

## Summary
Severity: Medium
Advisory: GHSA-qrgf-9gpc-vrxw
CVE: CVE-2023-27495
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-qrgf-9gpc-vrxw
Type: github-advisory

## Affected
- npm: `@fastify/csrf-protection` — affected >=0 <4.1.0
- npm: `@fastify/csrf-protection` — affected >=5.0.0 <6.3.0

## Details
## Description
The [CSRF](https://owasp.org/www-community/attacks/csrf) protection enforced by the `@fastify/csrf-protection` library in combination with `@fastify/cookie` can be bypassed from network and same-site attackers under certain conditions.

`@fastify/csrf-protection` supports an optional `userInfo` parameter that binds the CSRF token to the user. This parameter has been introduced to prevent cookie-tossing attacks as a fix for [CVE-2021-29624](https://www.cvedetails.com/cve/CVE-2021-29624). Whenever `userInfo` parameter is missing, or its value can be predicted for the target user account, network and [same-site](https://canitakeyoursubdomain.name/) attackers can 1. fixate a `_csrf` cookie in the victim's browser, and 2. forge CSRF tokens that are valid for the victim's session. This allows attackers to bypass the CSRF protection mechanism.

As a fix, `@fastify/csrf-protection` starting from version 6.3.0 (and v4.1.0) includes a server-defined secret `hmacKey` that cryptographically binds the CSRF token to the value of the `_csrf` cookie and the `userInfo` parameter, making tokens non-spoofable by attackers. This protection is effective as long as the `userInfo` parameter is unique for each user.

### Patches

This is patched in version 6.3.0 and v4.1.0.

### Workarounds

As a workaround, developers can use a random, non-predictable `userInfo` parameter for each user.

## Credits
* Pedro Adão (@pedromigueladao), [Instituto Superior Técnico, University of Lisbon](https://tecnico.ulisboa.pt/)
* Marco Squarcina (@lavish), [Security & Privacy Research Unit, TU Wien](https://secpriv.wien/)

## References
- https://github.com/fastify/csrf-protection/security/advisories/GHSA-qrgf-9gpc-vrxw
- https://github.com/fastify/csrf-protection/security/advisories/GHSA-rc4q-9m69-gqp8
- https://nvd.nist.gov/vuln/detail/CVE-2023-27495
- https://github.com/fastify/csrf-protection/commit/be3e5761f37aa05c7c1ac8ed44499c51ecec8058
- https://github.com/fastify/csrf-protection
- https://github.com/fastify/csrf-protection/releases/tag/v4.1.0
- https://github.com/fastify/csrf-protection/releases/tag/v6.3.0
- https://www.cvedetails.com/cve/CVE-2021-29624
