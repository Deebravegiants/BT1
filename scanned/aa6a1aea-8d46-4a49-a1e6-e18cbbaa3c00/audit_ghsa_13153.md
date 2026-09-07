# [M] Fiber unauthorized access vulnerability in `ctx.IsFromLocal()`

## Summary
Severity: Medium
Advisory: GHSA-3q5p-3558-364f
CVE: CVE-2023-41338
CWE: CWE-670
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-08
Source: https://github.com/advisories/GHSA-3q5p-3558-364f
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber` — affected >=0
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.49.2

## Details
### Impact
This vulnerability can be categorized as a security misconfiguration. It impacts users of our project who rely on the [ctx.IsFromLocal()](https://docs.gofiber.io/api/ctx#isfromlocal) method to restrict access to localhost requests. If exploited, it could allow unauthorized access to resources intended only for localhost.

In it's implementation it uses c.IPs():

```go
// IPs returns a string slice of IP addresses specified in the X-Forwarded-For request header.
// When IP validation is enabled, only valid IPs are returned.
func (c *Ctx) IPs() []string {
    return c.extractIPsFromHeader(HeaderXForwardedFor)
}
```

Thereby, setting `X-Forwarded-For: 127.0.0.1` in a request from a foreign host, will result in true for [ctx.IsFromLocal()](https://docs.gofiber.io/api/ctx#isfromlocal) 

### Patches
This issue has been patched in `v2.49.2` with commit [b8c9ede6efa231116c4bd8bb9d5e03eac1cb76dc](https://github.com/gofiber/fiber/commit/b8c9ede6efa231116c4bd8bb9d5e03eac1cb76dc)

### Workarounds
Currently, there are no known workarounds to remediate this vulnerability without upgrading to the patched version. We strongly advise users to apply the patch as soon as it is released.

### References
For further information and context regarding this security issue, please refer to the following resources:

- [Mozilla Developer Network - X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For)

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-3q5p-3558-364f
- https://nvd.nist.gov/vuln/detail/CVE-2023-41338
- https://github.com/gofiber/fiber/commit/b8c9ede6efa231116c4bd8bb9d5e03eac1cb76dc
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- https://docs.gofiber.io/api/ctx#isfromlocal
- https://github.com/gofiber/fiber
