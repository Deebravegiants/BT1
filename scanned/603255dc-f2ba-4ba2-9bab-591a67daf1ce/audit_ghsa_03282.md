# [M] Lack of protection against cookie tossing attacks in fastify-csrf

## Summary
Severity: Medium
Advisory: GHSA-rc4q-9m69-gqp8
CVE: CVE-2021-29624
CWE: CWE-352, CWE-565
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-rc4q-9m69-gqp8
Type: github-advisory

## Affected
- npm: `fastify-csrf` — affected >=0 <3.1.0

## Details
### Impact

Users that used fastify-csrf with the "double submit" mechanism using cookies with an application deployed across multiple subdomains, e.g. "heroku"-style platform as a service. 

### Patches

Version 3.1.0 of the fastify-csrf fixes it. 
See https://github.com/fastify/fastify-csrf/pull/51 and https://github.com/fastify/csrf/pull/2.

The user of the module would need to supply a `userInfo` when generating the CSRF token to fully implement the protection on their end. This is needed only for applications hosted on different subdomains.

### Workarounds

None available.

### References

1. https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
2. https://owasp.org/www-pdf-archive/David_Johansson-Double_Defeat_of_Double-Submit_Cookie.pdf

### Credits

This vulnerability was found by Xhelal Likaj <xhelallikaj20@gmail.com>.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [fastify-csrf](https://github.com/fastify/fastify-csrf)
* Email us at [hello@matteocollina.com](mailto:hello@matteocollina.com)

## References
- https://github.com/fastify/fastify-csrf/security/advisories/GHSA-rc4q-9m69-gqp8
- https://nvd.nist.gov/vuln/detail/CVE-2021-29624
- https://github.com/fastify/csrf/pull/2
- https://github.com/fastify/fastify-csrf/pull/51
- https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- https://github.com/fastify/fastify-csrf/releases/tag/v3.1.0
- https://owasp.org/www-pdf-archive/David_Johansson-Double_Defeat_of_Double-Submit_Cookie.pdf
