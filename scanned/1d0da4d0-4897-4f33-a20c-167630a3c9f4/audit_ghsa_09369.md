# [H] CrowdSec AppSec silently drops request body for chunked / HTTP-2 requests

## Summary
Severity: High
Advisory: GHSA-rw47-hm26-6wr7
CVE: CVE-2026-44982
CWE: CWE-693
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-rw47-hm26-6wr7
Type: github-advisory

## Affected
- Go: `github.com/crowdsecurity/crowdsec` — affected >=1.5.0 <1.7.8

## Details
## Summary

The CrowdSec AppSec component fails to read the HTTP request body for any request whose `Content-Length` is not positive — most notably HTTP/1.1 requests using `Transfer-Encoding: chunked` and HTTP/2 requests sent without a `content-length` header. Coraza is then evaluated against an empty body, so every WAF rule targeting `REQUEST_BODY`, `BODY_ARGS`, `ARGS_POST`, `JSON`, or `XML` silently fails to match.

An unauthenticated remote attacker can bypass the entire AppSec body-inspection pipeline  by changing a single framing header on an otherwise-malicious request. The bypassed request is forwarded as `allow` and produces no WAF log entry.

## Affected versions

- `github.com/crowdsecurity/crowdsec` — all releases up to and including **v1.7.7**.

## Affected component

`pkg/appsec/request.go`, function `NewParsedRequestFromRequest`.

## Root cause

```go
func NewParsedRequestFromRequest(r *http.Request, logger *log.Entry) (ParsedRequest, error) {
    var err error
    contentLength := max(r.ContentLength, 0)
    body := make([]byte, contentLength)
    if r.Body != nil {
        _, err = io.ReadFull(r.Body, body)
        if err != nil {
            return ParsedRequest{}, fmt.Errorf("unable to read body: %s", err)
        }
        r.Body = io.NopCloser(bytes.NewBuffer(body))
    }
    ...
}
```

Go's `net/http` server sets `r.ContentLength = -1` when the request uses `Transfer-Encoding: chunked` with no `Content-Length` header, or when an HTTP/2 request omits the `content-length` pseudo-header (DATA-frame-only body). With `ContentLength == -1`:

1. `max(-1, 0)` evaluates to `0`.
2. `make([]byte, 0)` allocates a zero-length slice.
3. `io.ReadFull` on a zero-length buffer needs zero bytes and returns immediately without touching `r.Body`.
4. The empty buffer is written back onto the request and onto the cloned request constructed later in the same function.

Every downstream consumer then sees an empty body. In the AppSec runner, `WriteRequestBody` is skipped because the parsed body has zero length, and `ProcessRequestBody` runs against nothing.

## Impact

Every body-scanning rule is bypassed for any request whose framing makes `Content-Length` non-positive. In default CrowdSec deployments using the standard AppSec collections, the bypass affects any rule with `zones` containing `BODY_ARGS`, `JSON`, `XML`, `REQUEST_BODY`, or `ARGS_POST`.

No configuration option mitigates the issue — the defect is in the request parser, not in any ruleset. Bypassed requests do not produce a WAF log entry, so operators have no signal that rules are being skipped.

Header-only and URI-only rules are unaffected.

## Workarounds

No complete workaround is available.

## References
- https://github.com/crowdsecurity/crowdsec/security/advisories/GHSA-rw47-hm26-6wr7
- https://github.com/crowdsecurity/crowdsec
