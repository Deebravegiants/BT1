### Title
Ineffective path-traversal sanitization in workflow HTTP fetcher allows request path to escape the intended base URL prefix - (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
`newHTTPFetcher()` builds outbound fetch URLs by joining a workflow-supplied `req.URL` (from `ghcapabilities.Request.URL`) onto an operator-configured `baseURL`, with a comment claiming the path is "cleaned...to prevent directory traversal." The actual sanitization only removes a leading `/` and calls `filepath.Clean`, which does not clamp `..` segments to the base directory — the same root-cause pattern as the reported laravel-mediable CVE (a partial/ineffective sanitizer that lets `..` survive and combine with a naive join/trim to escape the intended base path).

### Finding Description
In `newHTTPFetcher`: [1](#0-0) 

`cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")` only strips a leading slash; `filepath.Clean` does **not** remove leading `../` sequences from a relative path — it only collapses redundant separators/`.` and cancels `..` against *preceding* path components within the same string. Then `u.Path = filepath.Join(u.Path, cleanPath)` performs another `Clean`, which will pop directory components of `u.Path` (the base URL's path) for each surviving `..` in `cleanPath`. If the number of `..` segments in `req.URL` exceeds (or matches) the depth of `baseURL`'s path, the resulting `u.Path` escapes the operator-intended prefix entirely (e.g., landing outside the directory that was meant to scope allowed fetch targets on the remote host).

This mirrors the CVE's exact bug class: a supposed sanitizer (`sanitizePath()` there, `Clean`+`TrimPrefix` here) that looks like it blocks traversal but structurally cannot, because the dangerous `..` tokens are not stripped before being recombined with the base path via `Join`.

By contrast, the neighboring `newFileFetcher()` in the same file correctly guards against this by explicitly checking `strings.HasPrefix(fullPath, basePath+string(filepath.Separator))` after resolution — proving the file-fetcher path in this same file already validates this exact risk is real and must be checked; `newHTTPFetcher` lacks the equivalent post-join containment check. [2](#0-1) 

The `req.URL` value originates from `ghcapabilities.Request.URL`, a field documented as workflow-controlled ("URL to query, only http and https protocols are supported"): [3](#0-2) 

`FetcherService.Fetch` / the fetcher functions are invoked with this `req` for artifact/module retrieval as part of the workflow syncer flow reachable from a workflow spec.

### Impact Explanation
If the HTTP fetcher's `baseURL` is used to scope which remote resources a workflow is allowed to retrieve (e.g., a customer/tenant-scoped artifact prefix), a workflow author can craft a `URL` containing `..` segments to make the resolved request path escape that prefix and reach other paths on the same host — a cross-tenant/unauthorized-resource-read analog to the CVE's arbitrary-write. Since this fetcher operates on outbound requests only (not local filesystem writes), the concrete impact is confined to unauthorized read of resources served at other paths on the configured host, not remote code execution.

### Likelihood Explanation
Exploitability depends entirely on how restrictive the operator-configured `baseURL` path is and whether other paths on that host serve sensitive content; if `baseURL` has no path segments (root), there is nothing to escape, so likelihood is deployment-dependent. `req.URL` is attacker/workflow-owner-controlled, so the trigger requires no special privilege beyond registering a workflow.

### Recommendation
Do not rely on `filepath.Clean` + `TrimPrefix` alone. After joining, resolve the final URL path and verify (as `newFileFetcher` already does) that it remains within the intended base path using an explicit prefix check with a separator boundary, or reject any `req.URL` containing `..` path segments outright before joining.

### Proof of Concept
Given `baseURL = "https://artifacts.example.com/tenant-a/workflows"` and a malicious `ghcapabilities.Request{URL: "../../tenant-b/secret.wasm"}`:
1. `filepath.Clean("../../tenant-b/secret.wasm")` → `"../../tenant-b/secret.wasm"` (leading `..` preserved).
2. `TrimPrefix(..., "/")` is a no-op (no leading slash).
3. `filepath.Join("/tenant-a/workflows", "../../tenant-b/secret.wasm")` → `"/tenant-b/secret.wasm"`, escaping the `tenant-a/workflows` prefix.
4. The fetcher issues a GET to `https://artifacts.example.com/tenant-b/secret.wasm`, outside the intended scope.

### Citations

**File:** core/services/workflows/syncer/v2/fetcher.go (L222-231)
```go
		fullPath := filepath.Clean(u.Path)

		// ensure that the incoming request URL is either relative or absolute but within the basePath
		if !filepath.IsAbs(fullPath) {
			// If it's not absolute, we assume it's relative to the basePath
			fullPath = filepath.Join(basePath, fullPath)
		}
		if !strings.HasPrefix(fullPath, basePath+string(filepath.Separator)) && fullPath != basePath {
			return nil, fmt.Errorf("request URL %s is not within the basePath %s", fullPath, basePath)
		}
```

**File:** core/services/workflows/syncer/v2/fetcher.go (L248-259)
```go
	return func(ctx context.Context, messageID string, req ghcapabilities.Request) ([]byte, error) {
		// Clean the path to prevent directory traversal
		cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")

		// Join base URL with path
		u, err := url.Parse(baseURL)
		if err != nil {
			return nil, fmt.Errorf("failed to parse base URL: %w", err)
		}

		u.Path = filepath.Join(u.Path, cleanPath)
		fetchURL := u.String()
```

**File:** core/services/gateway/handlers/capabilities/webapi.go (L5-15)
```go
type Request struct {
	URL       string            `json:"url"`                 // URL to query, only http and https protocols are supported.
	Method    string            `json:"method,omitempty"`    // HTTP verb, defaults to GET.
	Headers   map[string]string `json:"headers,omitempty"`   // HTTP headers, defaults to empty.
	Body      []byte            `json:"body,omitempty"`      // HTTP request body
	TimeoutMs uint32            `json:"timeoutMs,omitempty"` // Timeout in milliseconds

	// Maximum number of bytes to read from the response body.  If the gateway max response size is smaller than this value, the gateway max response size will be used.
	MaxResponseBytes uint32 `json:"maxBytes,omitempty"`
	WorkflowID       string
}
```
