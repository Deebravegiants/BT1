# [M] Starlette: Arbitrary HTTP method dispatched to `HTTPEndpoint` attributes via `getattr`

## Summary
Severity: Medium
Advisory: GHSA-x746-7m8f-x49c
CVE: CVE-2026-48817
CWE: CWE-470
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-x746-7m8f-x49c
Type: github-advisory

## Affected
- PyPI: `starlette` — affected >=0 <1.1.0

## Details
### Summary

When dispatching a request, `HTTPEndpoint` selects the handler by lowercasing the HTTP method and looking it up as an attribute with `getattr`, without restricting the lookup to a known set of HTTP verbs.

When an `HTTPEndpoint` subclass is registered through `Route(...)` without an explicit `methods=` argument, the route does not constrain the method and every method reaches the endpoint. If a non-standard HTTP method whose lowercased name matches an attribute on the endpoint subclass reaches the endpoint, that attribute is invoked as if it were a request handler. An attacker can use this to reach methods that were never meant to be HTTP handlers, such as internal helpers, without the authorization checks applied by the intended public handler.

### Details

`HTTPEndpoint` uses the client-supplied method name to resolve an instance attribute, without validating it against the set of HTTP verbs the endpoint supports. A method such as `_DO_DELETE` therefore resolves an attribute like `_do_delete` and invokes it. Non-standard methods are valid [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110#name-method) token methods, so an endpoint must not treat the method name as a trusted attribute selector.

### Impact

An application is affected when all of the following hold:

* It defines an `HTTPEndpoint` subclass and registers it via `Route(...)` without an explicit `methods=` argument.
* The subclass defines additional methods whose names match a non-standard HTTP-method token shape and that accept a single `request` argument and return a response.

This also affects frameworks built on Starlette, like FastAPI.

### Mitigation

Register `HTTPEndpoint` subclasses with an explicit `methods=` argument on the `Route`, listing only the HTTP verbs the endpoint supports. The route then rejects any other method with `405 Method Not Allowed` before it reaches the endpoint, so non-standard methods cannot resolve an attribute.

## References
- https://github.com/Kludex/starlette/security/advisories/GHSA-x746-7m8f-x49c
- https://nvd.nist.gov/vuln/detail/CVE-2026-48817
- https://github.com/Kludex/starlette
- https://github.com/Kludex/starlette/releases/tag/1.1.0
