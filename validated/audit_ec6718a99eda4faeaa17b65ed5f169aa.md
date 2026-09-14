### Title
Path traversal in workflow syncer HTTP artifact fetcher allows requests outside intended base path - (`core/services/workflows/syncer/v2/fetcher.go`)

### Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds an outbound HTTP request URL by joining a configured `baseURL` path with an attacker/caller-supplied `req.URL` value using `filepath.Join`, without validating that the resulting path stays within the configured base path prefix. This mirrors the AWS SDK for PHP `buildEndpoint`/`UriResolver` bug class: dot-segment ("..") resolution silently collapses the joined path past the intended prefix, permitting the effective request path to escape the configured base path.

### Finding Description
In `newHTTPFetcher`: [1](#0-0) 

`req.URL` is cleaned with `filepath.Clean` and has a leading `/` stripped, but this does not prevent leading `../` segments from surviving in a relative path (e.g. `../../secret`). The result is then merged into the base URL's path via `filepath.Join(u.Path, cleanPath)`, which itself calls `path.Clean` on the combined string. For an absolute `u.Path` such as `/artifacts`, joining with `../../secret` collapses to `/secret` — escaping the `/artifacts` prefix entirely. Unlike the sibling function `newFileFetcher`, which explicitly re-validates the final path with a `strings.HasPrefix(fullPath, basePath+separator)` check before use: [2](#0-1) 

`newHTTPFetcher` has no equivalent bounds check after the join — the constructed `fetchURL` is sent directly to `http.NewRequestWithContext` and dispatched.

This is the same root cause pattern as CVE-2023-51651: a URI-building routine relies on lexical dot-segment stripping/resolution (RFC 3986-style) without re-verifying that the resolved path is still confined to the intended prefix/object-key namespace, letting attacker-supplied dot-segments (`..`) traverse outside the intended scope.

### Impact Explanation
`ghcapabilities.Request.URL` is the caller-supplied field: [3](#0-2) 

If this fetcher is reached with a `req.URL` value that is not fully trusted/sanitized by the caller (e.g. derived from a workflow spec or artifact reference supplied by a workflow owner/unprivileged client), an attacker could cause the node to issue requests to unintended paths on the configured artifact host, potentially retrieving objects/paths outside the sanctioned artifact directory on that host (e.g., internal-only paths served by the same host, or paths meant to be inaccessible). This is a request-path confinement bypass analogous to the S3 object-key traversal in the original advisory, though the concrete blast radius depends on what the configured `baseURL` host serves.

### Likelihood Explanation
I could not fully confirm, within the available index, which call sites feed externally influenced/attacker-controlled strings into `req.URL` for the HTTP-fetcher code path (`newHTTPFetcher`) versus only trusted/internal callers — I found `NewFetcherFunc` referenced in `core/cmd/shell.go` and test files, but was unable to trace the full upstream chain to confirm whether `req.URL` values reaching this exact function are attacker-influenced in a running node. Given the index's size limits, some call-graph context (especially in `core/cmd/shell.go` and any workflow-registry-driven artifact URL construction) may not be fully captured; a full-repository Devin session would be needed to trace this definitively.

### Recommendation
Apply the same prefix-confinement check used in `newFileFetcher` to `newHTTPFetcher`: after computing the joined path, verify (e.g. via `strings.HasPrefix`) that the resolved `u.Path` remains within the original base path before constructing and sending the request, rejecting any request whose resolved path escapes the configured prefix.

### Proof of Concept
Given a fetcher configured with `baseURL = "https://artifacts.example.com/allowed/"`, calling the returned `FetcherFunc` with `req.URL = "../../secret"` results in:
1. `cleanPath = "../../secret"` (no leading `/` to trim, so `filepath.Clean` leaves the leading `..` segments intact).
2. `u.Path = filepath.Join("/allowed", "../../secret")` → `"/secret"`.
3. `fetchURL = "https://artifacts.example.com/secret"` — outside the intended `/allowed/` prefix — is requested directly, with no post-join validation to reject it.

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
