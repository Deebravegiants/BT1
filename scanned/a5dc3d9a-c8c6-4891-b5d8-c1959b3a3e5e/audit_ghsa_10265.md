# [M] Fiber's cache middleware default key generator ignores query string, causing response mix-up across distinct query parameters

## Summary
Severity: Medium
Advisory: GHSA-35hp-hqmv-8qg8
CVE: CVE-2026-30246
CWE: CWE-200, CWE-436, CWE-524
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-35hp-hqmv-8qg8
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v3` — affected >=0 <3.2.0

## Details
### Summary
Fiber cache middleware's default key generator uses only `c.Path()` and does not include the query string.
As a result, requests like `/?id=1` and `/?id=2` can map to the same cache key and share the same cached response.

This can cause response mix-up (cache poisoning-like behavior) for endpoints where response content depends on query parameters.

### Details
Default configuration in cache middleware:

- `KeyGenerator: func(c fiber.Ctx) string { return utils.CopyString(c.Path()) }`

References:
- https://github.com/gofiber/fiber/blob/main/middleware/cache/config.go#L90-L92
- https://github.com/gofiber/fiber/blob/main/middleware/cache/cache_test.go#L599-L621

The existing test demonstrates that when handler output depends on query parameter `id`, a second request with a different query still returns the first cached response (cache hit), confirming query is not part of the default cache key.

### PoC
Minimal PoC:

```go
package main

import (
    "log"

    "github.com/gofiber/fiber/v3"
    "github.com/gofiber/fiber/v3/middleware/cache"
)

func main() {
    app := fiber.New()
    app.Use(cache.New()) // default config

    app.Get("/", func(c fiber.Ctx) error {
        return c.SendString(c.Query("id", "1"))
    })

    log.Fatal(app.Listen(":3000"))
}
```

Reproduction:

1. `GET /?id=1`
   - Cache miss
   - Response body: `1`
2. `GET /?id=2`
   - Cache hit
   - Response body: `1` (expected `2`)

Local verification command used:

```bash
go test ./middleware/cache -run Test_Cache_WithNoCacheRequestDirective -count=1
```

Observed result: test passes, confirming this is current behavior.

### Impact
- Responses that should vary by query parameters can be mixed between requests.
- In real deployments, this may leak or corrupt user/tenant-specific content if query parameters influence context or data selection.
- This is deployment-dependent but security-relevant, and not safe-by-default for query-variant responses.

### Suggested remediation
- Change default cache key generation to include path + normalized query string (or canonicalized original URL).
- Keep ability for custom key generators.
- Add explicit documentation warning that path-only keying is unsafe for query-dependent responses.

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-35hp-hqmv-8qg8
- https://nvd.nist.gov/vuln/detail/CVE-2026-30246
- https://github.com/gofiber/fiber/commit/050ff1ff18511c1475b8ec627460216aaecddd4e
- https://github.com/gofiber/fiber/commit/9a0d12c07ed895b84c72987f9288b04137afe5de
- https://github.com/gofiber/fiber
- https://github.com/gofiber/fiber/blob/main/middleware/cache/cache_test.go#L599-L621
- https://github.com/gofiber/fiber/blob/main/middleware/cache/config.go#L90-L92
