# [H] Overly permissive origin policy

## Summary
Severity: High
Advisory: GHSA-qxrj-hx23-xp82
CVE: CVE-2023-49803
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-11
Source: https://github.com/advisories/GHSA-qxrj-hx23-xp82
Type: github-advisory

## Affected
- npm: `@koa/cors` — affected >=0 <5.0.0

## Details
Currently, the middleware operates in a way that if an allowed origin is not provided, it will return an `Access-Control-Allow-Origin` header with the value of the origin from the request. This behavior completely disables one of the most crucial elements of browsers - the Same Origin Policy (SOP), this could cause a very serious security threat to the users of this middleware.

If such behavior is expected, for instance, when middleware is used exclusively for prototypes and not for production applications, it should be heavily emphasized in the documentation along with an indication of the risks associated with such behavior, as many users may not be aware of it.

## References
- https://github.com/koajs/cors/security/advisories/GHSA-qxrj-hx23-xp82
- https://nvd.nist.gov/vuln/detail/CVE-2023-49803
- https://github.com/koajs/cors/commit/f31dac99f5355c41e7d4dd3c4a80c5f154941a11
- https://github.com/koajs/cors
