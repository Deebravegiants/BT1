# [H] Session fixation in fastify-passport

## Summary
Severity: High
Advisory: GHSA-4m3m-ppvx-xgw9
CVE: CVE-2023-29019
CWE: CWE-384
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-4m3m-ppvx-xgw9
Type: github-advisory

## Affected
- npm: `@fastify/passport` — affected >=0 <1.1.0
- npm: `@fastify/passport` — affected >=2.0.0 <2.3.0

## Details
Applications using `@fastify/passport` for user authentication, in combination with `@fastify/session` as the underlying session management mechanism, are vulnerable to [session fixation attacks](https://owasp.org/www-community/attacks/Session_fixation) from network and same-site attackers.

## Details
fastify applications rely on the `@fastify/passport` library for user authentication. The login and user validation are performed by the `authenticate` function. When executing this function, the `sessionId` is preserved between the pre-login and the authenticated session. Network and [same-site attackers](https://canitakeyoursubdomain.name/) can hijack the victim's session by tossing a valid `sessionId` cookie in the victim's browser and waiting for the victim to log in on the website.

## Fix
As a solution, newer versions of `@fastify/passport` regenerate `sessionId` upon login, preventing the attacker-controlled pre-session cookie from being upgraded to an authenticated session.

## Credits
* Pedro Adão (@pedromigueladao), [Instituto Superior Técnico, University of Lisbon](https://tecnico.ulisboa.pt/)
* Marco Squarcina (@lavish), [Security & Privacy Research Unit, TU Wien](https://secpriv.wien/)

## References
- https://github.com/fastify/fastify-passport/security/advisories/GHSA-4m3m-ppvx-xgw9
- https://nvd.nist.gov/vuln/detail/CVE-2023-29019
- https://github.com/fastify/fastify-passport/commit/43c82c321db58ea3e375dd475de60befbfcf2a11
- https://github.com/fastify/fastify-passport
- https://owasp.org/www-community/attacks/Session_fixation
