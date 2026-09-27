# [C] Fiber has Insecure CORS Configuration, Allowing Wildcard Origin with Credentials

## Summary
Severity: Critical
Advisory: GHSA-fmg4-x8pw-hjhg
CVE: CVE-2024-25124
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-fmg4-x8pw-hjhg
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.52.1

## Details
The CORS middleware allows for insecure configurations that could potentially expose the application to multiple CORS-related vulnerabilities. Specifically, it allows setting the Access-Control-Allow-Origin header to a wildcard ("*") while also having the Access-Control-Allow-Credentials set to true, which goes against recommended security best practices.

## Impact
The impact of this misconfiguration is high as it can lead to unauthorized access to sensitive user data and expose the system to various types of attacks listed in the PortSwigger article linked in the references.

## Proof of Concept
The code in cors.go allows setting a wildcard in the AllowOrigins while having AllowCredentials set to true, which could lead to various vulnerabilities.

## Potential Solution
Here is a potential solution to ensure the CORS configuration is secure:

```go
func New(config ...Config) fiber.Handler {
    if cfg.AllowCredentials && cfg.AllowOrigins == "*" {
        panic("[CORS] Insecure setup, 'AllowCredentials' is set to true, and 'AllowOrigins' is set to a wildcard.")
    }
    // Return new handler goes below
}

The middleware will not allow insecure configurations when using `AllowCredentials` and `AllowOrigins`.
```

## Workarounds
For the meantime, users are advised to manually validate the CORS configurations in their implementation to ensure that they do not allow a wildcard origin when credentials are enabled. The browser fetch api, browsers and utilities that enforce CORS policies are not affected by this.

## References
[MDN Web Docs on CORS Errors](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors/CORSNotSupportingCredentials)
[CodeQL on CORS Misconfiguration](https://codeql.github.com/codeql-query-help/javascript/js-cors-misconfiguration-for-credentials/)
[PortSwigger on Exploiting CORS Misconfigurations](http://blog.portswigger.net/2016/10/exploiting-cors-misconfigurations-for.html)
[WhatWG CORS protocol and credentials ](https://fetch.spec.whatwg.org/#cors-protocol-and-credentials)

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-fmg4-x8pw-hjhg
- https://nvd.nist.gov/vuln/detail/CVE-2024-25124
- https://github.com/gofiber/fiber/commit/f0cd3b44b086544a37886232d0530601f2406c23
- https://codeql.github.com/codeql-query-help/javascript/js-cors-misconfiguration-for-credentials
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors/CORSNotSupportingCredentials
- https://fetch.spec.whatwg.org/#cors-protocol-and-credentials
- https://github.com/gofiber/fiber
- https://github.com/gofiber/fiber/releases/tag/v2.52.1
- https://saturncloud.io/blog/cors-cannot-use-wildcard-in-accesscontrolalloworigin-when-credentials-flag-is-true
- http://blog.portswigger.net/2016/10/exploiting-cors-misconfigurations-for.html
