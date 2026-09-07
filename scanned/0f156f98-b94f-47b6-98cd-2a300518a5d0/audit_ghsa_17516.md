# [M] chi Allows Host Header Injection which Leads to Open Redirect in RedirectSlashes

## Summary
Severity: Medium
Advisory: GHSA-vrw8-fxc6-2r93
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-vrw8-fxc6-2r93
Type: github-advisory

## Affected
- Go: `github.com/go-chi/chi/v5` — affected >=0 <5.2.2

## Details
### Summary
The RedirectSlashes function in middleware/strip.go is vulnerable to host header injection which leads to open redirect.

We consider this a **lower-severity** open redirect, as it can't be exploited from browsers or email clients (requires manipulation of a Host header).

### Details
The RedirectSlashes method uses the Host header to construct the redirectURL at this line https://github.com/go-chi/chi/blob/master/middleware/strip.go#L55

The Host header can be manipulated by a user to be any arbitrary host. This leads to open redirect when using the RedirectSlashes middleware

### PoC
Create a simple server which uses the RedirectSlashes middleware
```
package main

import (
	"fmt"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware" // Import the middleware package
)

func main() {
	// Create a new Chi router
	r := chi.NewRouter()

	// Use the built-in RedirectSlashes middleware
	r.Use(middleware.RedirectSlashes) // Use middleware.RedirectSlashes

	// Define a route handler
	r.Get("/", func(w http.ResponseWriter, r *http.Request) {
		// A simple response
		w.Write([]byte("Hello, World!"))
	})

	// Start the server
	fmt.Println("Starting server on :8080")
	http.ListenAndServe(":8080", r)
}
```
Run the server `go run main.go`

Once the server is running, send a request that will trigger the RedirectSlashes function with an arbitrary Host header
`curl -iL -H "Host: example.com" http://localhost:8080/test/`

Observe that the request will be redirected to example.com

```
curl -L -H "Host: example.com" http://localhost:8080/test/

<!doctype html>
<html>
<head>
    <title>Example Domain</title>

    <meta charset="utf-8" />
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style type="text/css">
    body {
        background-color: #f0f0f2;
        margin: 0;
        padding: 0;
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
... snipped ...
```
Without the host header, the response is returned from the test server
```
curl -L http://localhost:8080/test/

404 page not found
```

### Impact
An open redirect vulnerability allows attackers to trick users into visiting malicious sites. This can lead to phishing attacks, credential theft, and malware distribution, as users trust the application’s domain while being redirected to harmful sites.

### Potential mitigation
It seems that the purpose of the RedirectSlashes function is to redirect within the same application. In that case r.RequestURI can be used instead of r.Host by default. If there is a use case to redirect to a different host, a flag can be added to use the Host header instead. As this flag will be controlled by the developer they will make the decision of allowing redirects to arbitrary hosts  based on their judgement.

## References
- https://github.com/go-chi/chi/security/advisories/GHSA-vrw8-fxc6-2r93
- https://github.com/go-chi/chi/commit/1be7ad938cc9c5b39a9dea01a5c518848928ab65
- https://github.com/go-chi/chi
