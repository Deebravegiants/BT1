# [H] Fiber Crashes in BodyParser Due to Unvalidated Large Slice Index in Decoder

## Summary
Severity: High
Advisory: GHSA-qx2q-88mx-vhg7
CVE: CVE-2025-54801
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-05
Source: https://github.com/advisories/GHSA-qx2q-88mx-vhg7
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.52.9

## Details
### Description

When using Fiber's `Ctx.BodyParser` to parse form data containing a large numeric key that represents a slice index (e.g., `test.18446744073704`), the application crashes due to an out-of-bounds slice allocation in the underlying schema decoder.

The root cause is that the decoder attempts to allocate a slice of length `idx + 1` without validating whether the index is within a safe or reasonable range. If `idx` is excessively large, this leads to an integer overflow or memory exhaustion, causing a panic or crash.


### Steps to Reproduce

Create a POST request handler that accepts `x-www-form-urlencoded` data

```go
package main

import (
	"fmt"
	"net/http"

	"github.com/gofiber/fiber/v2"
)

type RequestBody struct {
	NestedContent []*struct{} `form:"test"`
}

func main() {
	app := fiber.New()

	app.Post("/", func(c *fiber.Ctx) error {
		formData := RequestBody{}
		if err := c.BodyParser(&formData); err != nil {
			fmt.Println(err)
			return c.SendStatus(http.StatusUnprocessableEntity)
		}
		return nil
	})

	fmt.Println(app.Listen(":3000"))
}

```

Run the server and send a POST request with a large numeric key in form data, such as:

```bash
curl -v -X POST localhost:3000 --data-raw 'test.18446744073704' \
  -H 'Content-Type: application/x-www-form-urlencoded'
```


### Relevant Code Snippet

Within the decoder's [decode method](https://github.com/gofiber/fiber/blob/v2.52.8/internal/schema/decoder.go#L249):

```go
idx := parts[0].index
if v.IsNil() || v.Len() < idx+1 {
    value := reflect.MakeSlice(t, idx+1, idx+1)  // <-- Panic/crash occurs here when idx is huge
    if v.Len() < idx+1 {
        reflect.Copy(value, v)
    }
    v.Set(value)
}
```

The `idx` is not validated before use, leading to unsafe slice allocation for extremely large values.

---

### Impact

- Application panic or crash on malicious or malformed input.
- Potential denial of service (DoS) via memory exhaustion or server crash.
- Lack of defensive checks in the parsing code causes instability.

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-qx2q-88mx-vhg7
- https://nvd.nist.gov/vuln/detail/CVE-2025-54801
- https://github.com/gofiber/fiber/commit/e115c08b8f059a4a031b492aa9eef0712411853d
- https://github.com/gofiber/fiber
