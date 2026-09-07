# [H] Fiber has an Arbitrary File Read in Static Middleware on Windows

## Summary
Severity: High
Advisory: GHSA-m3c2-496v-cw3v
CVE: CVE-2026-25891
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-m3c2-496v-cw3v
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v3` — affected >=0 <3.1.0

## Details
### Summary

**Description**
A Path Traversal (CWE-22) vulnerability in Fiber allows a remote attacker to bypass the static middleware sanitizer and read arbitrary files on the server file system on Windows. This affects Fiber v3 through version 3.0.0. This has been patched in Fiber v3 version 3.1.0.
 
### Details
The vulnerability resides in `middleware/static/static.go` within the `sanitizePath` function. This function attempts to sanitize the requested path by checking for backslashes, decoding the URL, and then cleaning the path.

The vulnerability stems from two combined issues:
- The check for backslash characters happens before the URL decoding loop. If an attacker sends a double-encoded backslash, the initial check sees `%255C` and passes. The loop then decodes this into a single backslash.
- The function uses `path.Clean` to clean the resulting string. `path.Clean` is designed for slash-separated paths  and does not recognize backslashes as directory separators. Consequently, sequences like `..\..\` are treated as valid filenames.

When this sanitized path is later used, the backslashes are interpreted as valid separators, allowing the attacker to traverse up the directory tree.
```go
// pkg/static/static.go
func sanitizePath(p []byte, filesystem fs.FS) ([]byte, error) {
    ...
    // this check happens BEFORE decoding
    if bytes.IndexByte(p, '\\') >= 0 {
        ...
    } 
    // This loop decodes %255C to %5C to \
    for strings.IndexByte(s, '%') >= 0 {
        us, err := url.PathUnescape(s)
        ...
        s = us
    }
    // path.Clean only understands forward slashes (/)
    s = pathpkg.Clean("/" + s)
    ...
    return utils.UnsafeBytes(s), nil
}
```

### Impact

This impacts Fiber v3 prereleases through stable release version 3.0.0.

Successful exploitation requires the server to be using the static middleware on Windows, as this is the only OS where backslashes are treated as directory separators by the file system.

Exploitation allows directory traversal on the host server. An attacker can read arbitrary files within the scope of the application server context. Depending on permissions and deployment conditions, attackers may access sensitive files outside the web root, such as configuration files, source code, or system files. Leaking application secrets often leads to further compromise.

### Patches

This has been [patched](https://github.com/gofiber/fiber/pull/4064) in Fiber v3 version 3.1.0.  Users are strongly encouraged to update to the latest available release.

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-m3c2-496v-cw3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-25891
- https://github.com/gofiber/fiber/pull/4064
- https://github.com/gofiber/fiber/commit/59133702301c2ab7b776dd123b474cbd995f2c86
- https://github.com/gofiber/fiber
- https://pkg.go.dev/vuln/GO-2026-4540
