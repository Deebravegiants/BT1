# [H] Cross-Site Request Forgery (CSRF) in FastAPI

## Summary
Severity: High
Advisory: GHSA-8h2j-cgx8-6xv7
CVE: CVE-2021-32677
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2021-06-10
Source: https://github.com/advisories/GHSA-8h2j-cgx8-6xv7
Type: github-advisory

## Affected
- PyPI: `fastapi` — affected >=0 <0.65.2

## Details
### Impact

FastAPI versions lower than `0.65.2` that used cookies for authentication in path operations that received JSON payloads sent by browsers were vulnerable to a Cross-Site Request Forgery (CSRF) attack.

In versions lower than `0.65.2`, FastAPI would try to read the request payload as JSON even if the `content-type` header sent was not set to `application/json` or a compatible JSON media type (e.g. `application/geo+json`).

So, a request with a content type of `text/plain` containing JSON data would be accepted and the JSON data would be extracted.

But requests with content type `text/plain` are exempt from [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) preflights, for being considered [Simple requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests). So, the browser would execute them right away including cookies, and the text content could be a JSON string that would be parsed and accepted by the FastAPI application.

### Patches

This is fixed in FastAPI `0.65.2`.

The request data is now parsed as JSON only if the `content-type` header is `application/json` or another JSON compatible media type like `application/geo+json`.

### Workarounds

It's best to upgrade to the latest FastAPI.

But still, it would be possible to add a middleware or a dependency that checks the `content-type` header and aborts the request if it is not `application/json` or another JSON compatible content type.

### References

* [CORS on Mozilla web docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
* [This answer on StackExchange](https://security.stackexchange.com/questions/157528/ways-to-bypass-browsers-cors-policy/157531#157531)
* [OWASP CSRF](https://owasp.org/www-community/attacks/csrf)
* Fixed in PR [#2118](https://github.com/tiangolo/fastapi/pull/2118)

### For more information

If you have any questions or comments, write to [security@tiangolo.com](mailto:security@tiangolo.com)

## References
- https://github.com/tiangolo/fastapi/security/advisories/GHSA-8h2j-cgx8-6xv7
- https://nvd.nist.gov/vuln/detail/CVE-2021-32677
- https://github.com/tiangolo/fastapi/commit/fa7e3c996edf2d5482fff8f9d890ac2390dede4d
- https://github.com/pypa/advisory-database/tree/main/vulns/fastapi/PYSEC-2021-100.yaml
- https://github.com/tiangolo/fastapi
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MATAWX25TYKNEKLDMKWNLYDB34UWTROA
