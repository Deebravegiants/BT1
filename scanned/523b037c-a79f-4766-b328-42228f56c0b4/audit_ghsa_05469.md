# [M] chi has an open redirect vulnerability in the RedirectSlashes middleware

## Summary
Severity: Medium
Advisory: GHSA-mqqf-5wvp-8fh8
CVE: CVE-2025-69725
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-mqqf-5wvp-8fh8
Type: github-advisory

## Affected
- Go: `github.com/go-chi/chi/v5` — affected >=5.2.2 <5.2.4

## Details
### Summary

The `RedirectSlashes` function in middleware/strip.go does not perform correct input validation and can lead to an open redirect vulnerability.

### Details

The `RedirectSlashes` function performs a `Trim` to all forward slash (`/`) characters, while prepending a single one at the begining of the path (Line 52).

However, it does not trim backslashes (`\`).

```go
File: middleware/strip.go
41: func RedirectSlashes(next http.Handler) http.Handler {
...
51: 			// Trim all leading and trailing slashes (e.g., "//evil.com", "/some/path//")
52: 			path = "/" + strings.Trim(path, "/")
...
62: }
```

Also, from version 5.2.2 onwards the `RedirectSlashes` function does not take into consideration the `Host` Header in the redirect response returned. This was done in order to combat another [[vulnerability](https://github.com/go-chi/chi/security/advisories/GHSA-vrw8-fxc6-2r93)](https://github.com/go-chi/chi/security/advisories/GHSA-vrw8-fxc6-2r93).

The above make it possible for a response in the following form:

```
HTTP/1.1 301 Moved Permanently
Location: /\evil.com
```

The `/\evil.com` will be transformed by most browsers (Chrome, Firefox, etc. not Safari) into `//evil.com` which is a protocol relative URL and will result in a redirect to `evil.com`, essentially making it an open redirect vulnerability.

### PoC

A minimal working example can be seen below.

```go
package main

import (
	"fmt"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)



func main() {
	r := chi.NewRouter()

	r.Use(middleware.RedirectSlashes)

	r.Get("/*", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	fmt.Println("Server starting on port 8081...")
	if err := http.ListenAndServe(":8081", r); err != nil {
		fmt.Printf("Error starting server: %v\n", err)
	}
}

```

And when we request the path `/\evil.com` (needs a second backslash or URL encoding in the terminal), the HTTP Redirect Location is just `/\evil.com` without any domain/Host information.

```bash
$ curl -I  localhost:8081/\\evil.com/
HTTP/1.1 301 Moved Permanently
Content-Type: text/html; charset=utf-8
Location: /\evil.com
```

```bash
$ curl -I  localhost:8081/%5Cevil.com/
HTTP/1.1 301 Moved Permanently
Content-Type: text/html; charset=utf-8
Location: /\evil.com
```

This opened in a browser (Chrome, Firefox) will result in a transformation to `//evil.com` which in turn will result in a redirect to `evil.com`.
<img width="200" alt="image-20250829115619807" src="https://github.com/user-attachments/assets/44aedad1-64b6-4660-8b26-fad9b4eca036" />


<img width="200" alt="image-20250829115632067" src="https://github.com/user-attachments/assets/b976d47d-1975-469c-abd3-deb907a68db2" />


### Impact

This essentially consists of an open redirect vulnerability, provided that victim users use the most popular browsers (Chrome, Firefox, etc. It does not work in e.g. Safari).

The attacker can construct a malicious URL on a domain of a legitimate website and send it to the victim user. The victim users thinking that they will click on a legitimate website's URL, they will unknowingly be reidrected to an attacker controlled website.

This can lead to credential theft if the victim gets redirected to a phishing website, to malware that is hosted on the attacker controlled website etc. Also, it has a greate reputation / business impact for the affected legitimate website.

In order to exploit this vulnerability the attacker does not need to be authenticated or have ay other priviledge / knowledge regarding the affected application.

CVSS Score: [4.7 (Medium)](https://www.first.org/cvss/calculator/3-0#CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N)

## References
- https://github.com/go-chi/chi/security/advisories/GHSA-mqqf-5wvp-8fh8
- https://nvd.nist.gov/vuln/detail/CVE-2025-69725
- https://github.com/go-chi/chi/issues/1037
- https://github.com/go-chi/chi/commit/6eb35881c0e438ffb663ddbad3a61babaa5e5d8a
- https://github.com/go-chi/chi
- http://go-chichi.com
