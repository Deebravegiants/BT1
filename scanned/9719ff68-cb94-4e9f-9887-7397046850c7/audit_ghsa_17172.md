# [C] Authorization Bypass Through User-Controlled Key in go-zero

## Summary
Severity: Critical
Advisory: GHSA-fgxv-gw55-r5fq
CVE: CVE-2024-27302
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-04
Source: https://github.com/advisories/GHSA-fgxv-gw55-r5fq
Type: github-advisory

## Affected
- Go: `github.com/zeromicro/go-zero` — affected >=0 <1.4.4

## Details
### Summary
Hello go-zero maintainer team, I would like to report a security concerning your CORS Filter feature. 

### Details
Go-zero allows user to specify a [CORS Filter](https://github.com/zeromicro/go-zero/blob/master/rest/internal/cors/handlers.go) with a configurable allows param - which is an array of domains allowed in CORS policy.

However, the `isOriginAllowed` uses `strings.HasSuffix` to check the origin, which leads to bypass via domain like `evil-victim.com`
```go
func isOriginAllowed(allows []string, origin string) bool {
	for _, o := range allows {
		if o == allOrigins {
			return true
		}

		if strings.HasSuffix(origin, o) {
			return true
		}
	}

	return false
}
```

### PoC
Use code below as a PoC. Only requests from `safe.com` should bypass the CORS Filter
```go
package main

import (
	"errors"
	"net/http"

	"github.com/zeromicro/go-zero/rest"
)

func main() {
	svr := rest.MustNewServer(rest.RestConf{Port: 8888}, rest.WithRouter(mockedRouter{}), rest.WithCors("safe.com"))
	svr.Start()
}

type mockedRouter struct{}

// some sensitive path
func (m mockedRouter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// check user's cookie
	// ...
	// return sensitive data
	w.Write([]byte("social_id: 420101198008292930"))
}

func (m mockedRouter) Handle(_, _ string, handler http.Handler) error {
	return errors.New("foo")
}

func (m mockedRouter) SetNotFoundHandler(_ http.Handler) {
}

func (m mockedRouter) SetNotAllowedHandler(_ http.Handler) {
}
```
Send a request to localhost:8888 with `Origin:not-safe.com`
You can see the origin reflected in response, which bypass the CORS Filter
![image](https://user-images.githubusercontent.com/70683161/221365842-9d76a3a4-a79d-413a-85b7-06b50b0a7807.png)

### Impact
This vulnerability is capable of breaking CORS policy and thus allowing any page to make requests, retrieve data on behalf of other users.

## References
- https://github.com/zeromicro/go-zero/security/advisories/GHSA-fgxv-gw55-r5fq
- https://nvd.nist.gov/vuln/detail/CVE-2024-27302
- https://github.com/zeromicro/go-zero/commit/d9d79e930dff6218a873f4f02115df61c38b15db
- https://github.com/zeromicro/go-zero
