# [M] CSRF token fixation in fastify-passport

## Summary
Severity: Medium
Advisory: GHSA-2ccf-ffrj-m4qw
CVE: CVE-2023-29020
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-2ccf-ffrj-m4qw
Type: github-advisory

## Affected
- npm: `@fastify/passport` — affected >=0 <1.1.0
- npm: `@fastify/passport` — affected >=2.0.0 <2.3.0

## Details
The [CSRF](https://owasp.org/www-community/attacks/csrf) protection enforced by the `@fastify/csrf-protection` library, when combined with `@fastify/passport`, can be bypassed by network and same-site attackers.

## Details
`fastify/csrf-protection` implements the [synchronizer token pattern](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#synchronizer-token-pattern) (using plugins `@fastify/session` and `@fastify/secure-session`) by storing a random value used for CSRF token generation in the `_csrf` attribute of a user's session.

The `@fastify/passport` library does not clear the session object upon authentication, preserving the `_csrf` attribute between pre-login and authenticated sessions. Consequently, CSRF tokens generated before authentication are still valid. Network and [same-site attackers](https://canitakeyoursubdomain.name/) can thus obtain a CSRF token for their pre-session, fixate that pre-session in the victim's browser via cookie tossing, and then perform a CSRF attack after the victim authenticates.

## Fix
As a solution, newer versions of `@fastify/passport` include the configuration options

* `clearSessionOnLogin (default: true)` and
* `clearSessionIgnoreFields (default: ['session'])`

to clear all the session attributes by default, preserving those explicitly defined in `clearSessionIgnoreFields`.

## Credits
* Pedro Adão (@pedromigueladao), [Instituto Superior Técnico, University of Lisbon](https://tecnico.ulisboa.pt/)
* Marco Squarcina (@lavish), [Security & Privacy Research Unit, TU Wien](https://secpriv.wien/)

## References
- https://github.com/fastify/fastify-passport/security/advisories/GHSA-2ccf-ffrj-m4qw
- https://nvd.nist.gov/vuln/detail/CVE-2023-29020
- https://github.com/fastify/fastify-passport/commit/07c90feab9cba0dd4779e47cfb0717a7e2f01d3d
- https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#synchronizer-token-pattern
- https://github.com/fastify/fastify-passport
- https://owasp.org/www-community/attacks/csrf
