# [M] gorilla/csrf CSRF vulnerability due to broken Referer validation

## Summary
Severity: Medium
Advisory: GHSA-rq77-p4h8-4crw
CVE: CVE-2025-24358
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-14
Source: https://github.com/advisories/GHSA-rq77-p4h8-4crw
Type: github-advisory

## Affected
- Go: `github.com/gorilla/csrf` — affected >=0 <1.7.3

## Details
### Summary

gorilla/csrf is vulnerable to CSRF via form submission from origins that share a top level domain with the target origin.

### Details

gorilla/csrf does not validate the Origin header against an allowlist. Its executes its validation of the Referer header for cross-origin requests only when it believes the request is being served over TLS. It determines this by inspecting the `r.URL.Scheme` value. However, this value is never populated for "server" requests [per the Go spec](https://pkg.go.dev/net/http#Request), and so this check does not run in practice. 
```
	// URL specifies either the URI being requested (for server
	// requests) or the URL to access (for client requests).
	//
	// For server requests, the URL is parsed from the URI
	// supplied on the Request-Line as stored in RequestURI.  For
	// most requests, fields other than Path and RawQuery will be
	// empty. (See [RFC 7230, Section 5.3](https://rfc-editor.org/rfc/rfc7230.html#section-5.3))
	//
	// For client requests, the URL's Host specifies the server to
	// connect to, while the Request's Host field optionally
	// specifies the Host header value to send in the HTTP
	// request.
	URL *[url](https://pkg.go.dev/net/url).[URL](https://pkg.go.dev/net/url#URL)
```

### PoC

- create trusted origin `target.example.test` protected with gorilla/csrf and served over TLS hosting form on `/submit`
- create attacker origin `attack.example.test` served over TLS
- attacker exfiltrates token & cookie combination from `target.example.test` 
- attacker sets exfiltrated cookie with `domain=.example.test and path=/submit`
  - as the cookie has a more specific path than `/` (the default for CSRF cookies) it will be sent first by the browser on submit to our target origin
- submit form from `attack.example.test` with exfiltrated CSRF form token
- observe valid form submission as `attack.example.test` Origin / Referer headers are not validated. 

### Impact

This vulnerability allows an attacker who has gained XSS on a subdomain or top level domain to perform authenticated form submissions against gorilla/csrf protected targets that share the same top level domain.

This bug has existed in gorilla/csrf since its initial release in 2015.

## References
- https://github.com/gorilla/csrf/security/advisories/GHSA-rq77-p4h8-4crw
- https://nvd.nist.gov/vuln/detail/CVE-2025-24358
- https://github.com/gorilla/csrf/commit/9dd6af1f6d30fc79fb0d972394deebdabad6b5eb
- https://github.com/gorilla/csrf
- https://lists.debian.org/debian-lts-announce/2025/05/msg00002.html
- https://pkg.go.dev/vuln/GO-2025-3607
