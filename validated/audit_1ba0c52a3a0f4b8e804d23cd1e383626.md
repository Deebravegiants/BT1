## Analysis

I found a structurally similar bug-class match to the rclone CVE (path.Join(root, remote) allowing `..` segments to escape a configured root) in the workflow artifact fetcher.

### Title
Missing root-containment check in HTTP artifact fetcher allows path traversal outside configured base path - (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
`core/services/workflows/syncer/v2/fetcher.go` implements two `FetcherFunc` variants created by `NewFetcherFunc`: `newFileFetcher` for `file://` base URLs and `newHTTPFetcher` for `http(s)://` base URLs [1](#0-0) . Both are designed to constrain an externally-supplied `req.URL` to a path underneath an operator-configured base location, mirroring the rclone `path.Join(root, remote)` pattern that the CVE describes.

### Finding Description
`newFileFetcher` correctly re-validates the joined path against the base path before use: [2](#0-1) 

`newHTTPFetcher`, however, only cleans the incoming value and joins it into the URL's path with no equivalent post-join containment check: [3](#0-2) 

`filepath.Clean` does not strip leading `..` segments from a relative path (e.g. `Clean("../../etc/passwd")` stays `"../../etc/passwd"`), and `strings.TrimPrefix(..., "/")` only removes a single leading slash. The subsequent `filepath.Join(u.Path, cleanPath)` then collapses those `..` segments against `u.Path`, which can walk the resulting request path outside the intended base path segment (e.g. `/artifacts`) to an arbitrary path on the same host — the same class of flaw as rclone's `path.Join(root, remote)` before `EncodeDot`, just applied to an HTTP path prefix instead of a storage-backend root.

`req.URL` here is populated from workflow artifact locations (`binaryURL` / `configURL`) that originate from on-chain `WorkflowRegisteredEvent` data and are passed straight into `ghcapabilities.Request.URL` and then into the fetcher: [4](#0-3) [5](#0-4) . Whoever can register a workflow (and thus set these URLs) is an unprivileged actor relative to the node's fetch logic.

### Impact Explanation
If an operator configures `NewFetcherFunc` with an `http(s)://` base URL to bypass the gateway (per the function's own comment, "bypasses the gateway"), an unprivileged workflow-registrant-controlled `binaryURL`/`configURL` value containing `../` segments can cause the node to issue its artifact-fetch request against a different path on the configured artifact host than the one the operator intended to expose, rather than the intended sandboxed prefix. This is a path/prefix confinement bypass analogous in root cause to the rclone advisory, though scoped to path segments on a fixed host rather than a different bucket/share.

### Likelihood Explanation
Requires: (1) the deployment uses the `http(s)://` `NewFetcherFunc` override path rather than the standard gateway flow, and (2) an actor able to register a workflow (or otherwise influence `binaryURL`/`configURL`) supplies a traversal payload. Given `newFileFetcher`'s equivalent guard already anticipates and blocks exactly this kind of traversal (as proven by its dedicated test case), the absence of the same guard in `newHTTPFetcher` looks like an inconsistency/gap rather than an intentional design decision.

### Recommendation
Add the same base-path containment check used in `newFileFetcher` to `newHTTPFetcher` — after joining, verify the resulting `u.Path` still has the original base path as a prefix (or otherwise reject `req.URL` values containing `..` segments) before issuing the HTTP request.

### Proof of Concept
1. Configure the fetcher override with `baseURL = "https://artifact-host.example.com/artifacts"`.
2. Register/trigger a workflow whose `binaryURL` (or `configURL`) resolves to a `req.URL` value equivalent to `"../internal/admin"`.
3. In `newHTTPFetcher`, `cleanPath` becomes `"../internal/admin"`, and `filepath.Join("/artifacts", "../internal/admin")` yields `"/internal/admin"`, causing the node to fetch `https://artifact-host.example.com/internal/admin` instead of a path constrained to `/artifacts/...`, with no containment check rejecting it (unlike `newFileFetcher`'s explicit `HasPrefix` check) [6](#0-5) .

**Note on completeness:** I was unable to fully confirm, within the available exploration budget, whether every deployment path always uses the gateway-mediated `Fetch` (which is unaffected) versus the `NewFetcherFunc` HTTP override in production configurations, so real-world reachability of this specific code path should be verified further.

### Citations

**File:** core/services/workflows/syncer/v2/fetcher.go (L172-196)
```go
// NewFetcher creates a new FetcherFunc based on the provided URL configuration
// The implementation supports both file and HTTP(S) URLs and bypasses the gateway
func NewFetcherFunc(baseURL string, lggr logger.Logger) (types.FetcherFunc, error) {
	if baseURL == "" {
		return nil, errors.New("baseURL cannot be empty")
	}

	u, err := url.Parse(baseURL)
	if err != nil {
		return nil, fmt.Errorf("invalid URL: %w", err)
	}

	switch u.Scheme {
	case "file":
		// Ensure the basePath is absolute
		if !filepath.IsAbs(u.Path) {
			return nil, fmt.Errorf("basePath must be an absolute path, got: %s", u.Path)
		}
		return newFileFetcher(u.Path, lggr), nil
	case "http", "https":
		return newHTTPFetcher(baseURL, lggr), nil
	default:
		return nil, fmt.Errorf("unsupported URL scheme: %s", u.Scheme)
	}
}
```

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-259)
```go
func newHTTPFetcher(baseURL string, lggr logger.Logger) types.FetcherFunc {
	client := &http.Client{
		Timeout: 30 * time.Second,
	}

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

**File:** core/services/workflows/artifacts/v2/store.go (L174-183)
```go
	req := ghcapabilities.Request{
		URL:              binaryURL,
		Method:           http.MethodGet,
		MaxResponseBytes: safeUint32(uint64(maxBinarySize)),
		WorkflowID:       workflowID,
	}
	binary, err = h.fetchFn(ctx, messageID(binaryURL, workflowID), req)
	if err != nil {
		return nil, nil, &types.ArtifactFetchError{ArtifactType: "binary", URL: binaryURL, Err: err}
	}
```

**File:** core/services/workflows/artifacts/v2/store.go (L217-227)
```go
		req := ghcapabilities.Request{
			URL:              configURL,
			Method:           http.MethodGet,
			MaxResponseBytes: safeUint32(uint64(maxResponseBytes)),
			WorkflowID:       workflowID,
		}

		config, err2 = h.fetchFn(ctx, messageID(configURL, workflowID), req)
		if err2 != nil {
			return nil, nil, &types.ArtifactFetchError{ArtifactType: "config", URL: configURL, Err: err2}
		}
```
