# [M] CRLF vulnerability in Fiber

## Summary
Severity: Medium
Advisory: GHSA-9cx9-x2gp-9qvh
CVE: CVE-2020-15111
CWE: CWE-74, CWE-93
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-9cx9-x2gp-9qvh
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber` — affected >=0 <1.12.6

## Details
### Impact
The filename that is given in [c.Attachment()](https://docs.gofiber.io/ctx#attachment) is not escaped, and therefore vulnerable for a CRLF injection attack. I.e. an attacker could upload a custom filename and then give the link to the victim. With this filename, the attacker can change the name of the downloaded file, redirect to another site, change the authorization header, etc.

### Steps to reproduce
```go
package main

import "github.com/gofiber/fiber"

const badFileName = "another secret document.pdf\"\r\nLocation: google.com\r\nAuthorization: \"example_of_session_fixation"

func splitTheResponse(c *fiber.Ctx) {
	c.Attachment(badFileName)
}

func main() {
	app := fiber.New()
	app.Get("/attack", splitTheResponse)
	app.Listen("127.0.0.1:8080")
}
```
```
HTTP/1.1 200 OK
Date: Fri, 10 Jul 2020 19:47:04 GMT
Content-Type: application/octet-stream
Content-Length: 0
Content-Disposition: attachment; filename="another secret document.pdf"
Location: google.com
Authorization: "example_of_session_fixation"
```

### Patches
This issue has been patched in `v1.12.6` with commit [579](https://github.com/gofiber/fiber/pull/579/commits/f698b5d5066cfe594102ae252cd58a1fe57cf56f) escaping the filename by default.

### Workarounds
You could of course serialize the input yourself before passing it to `ctx.Attachment()`, this is actually a good practice by default. But in case you forget, we got you covered 👍 

### References
A CRLF injection attack is one of several types of injection attacks. It can be used to escalate to more malicious attacks such as Cross-site Scripting (XSS), page injection, web cache poisoning, cache-based defacement, and more. A CRLF injection vulnerability exists if an attacker can inject the CRLF characters into a web application, for example using a user input form or an HTTP request, [see acunetix](https://www.acunetix.com/websitesecurity/crlf-injection/)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [gofiber/fiber](https://github.com/gofiber/fiber)
* Join us on [Discord](https://gofiber.io/discord)

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-9cx9-x2gp-9qvh
- https://nvd.nist.gov/vuln/detail/CVE-2020-15111
- https://github.com/gofiber/fiber/pull/579
- https://github.com/gofiber/fiber/commit/f698b5d5066cfe594102ae252cd58a1fe57cf56f
- https://github.com/gofiber/fiber
- https://pkg.go.dev/vuln/GO-2021-0108
