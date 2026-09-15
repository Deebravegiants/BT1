### Title
Path traversal in `newHTTPFetcher` bypasses base-URL path restriction, allowing artifact fetches to escape configured path prefix - (File: core/services/workflows/syncer/v2/fetcher.go)

### Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` is meant to restrict fetched resources to paths under an operator-configured `baseURL`, but it resolves the request path with `filepath.Join`/`filepath.Clean` in a way that does not correctly bound the result to the base path, mirroring the same bug class as the reported Node.js `fs.writeFileSync`/experimental-permission traversal (a directory-prefix check defeated by unresolved `..` segments).

### Finding Description
`NewFetcherFunc` builds either a file-based or HTTP-based fetcher restricted to a configured base location: [1](#0-0) 

For the HTTP case, `newHTTPFetcher` attempts to prevent directory traversal by cleaning the incoming `req.URL` and joining it onto the base URL's path: [2](#0-1) 

The flaw: `filepath.Clean` on a purely relative string that starts with `..` (e.g. `"../../etc/passwd"`) cannot remove the leading `..` segments (there is nothing above the relative root to cancel them against), so `cleanPath` still contains literal `..` components after `TrimPrefix(..., "/")`. The subsequent `filepath.Join(u.Path, cleanPath)` re-invokes `Clean` on the *combined absolute* path, and Go's `path/filepath` semantics resolve `..` against the leading path segments freely — this lets the `..` sequences walk back up above `u.Path` (the operator-configured base path) and even past it, producing a `fetchURL` outside the intended path prefix. Unlike `newFileFetcher`, which validates the final resolved path against `basePath` with an explicit `strings.HasPrefix(fullPath, basePath+separator)` check (the correct fix pattern, matching CVE-2023-30584's remediation), `newHTTPFetcher` performs no post-join containment check at all — it blindly trusts that `Clean`+`Join` bound the path, which they do not for attacker-supplied leading `..` segments.

This is the exact bug class from the report: a path-restriction feature (`--allow-fs-write=<dir>` in Node.js; a configured `baseURL` here) is defeated because the traversal-prevention logic runs before or without a proper post-resolution prefix check.

### Impact Explanation
The `req.URL` fed into the fetcher (`ghcapabilities.Request.URL`) is populated from `BinaryURL`/`ConfigURL` in `WorkflowRegisteredEvent`, which come from on-chain workflow registrations: [3](#0-2) [4](#0-3) 

Any address that can register a workflow on the Workflow Registry contract (an unprivileged, non-operator actor from the node's perspective) controls this URL. If a node/operator configures the syncer to fetch workflow artifacts via a restricted HTTP base URL (`newFetcherFunc`/`newHTTPFetcher`) instead of the gateway-routed default, a malicious workflow owner can supply a `BinaryURL`/`ConfigURL` containing `../` sequences to make the node issue HTTP requests to resources outside the intended base path/host-path prefix — potentially reaching internal-network paths or unintended endpoints reachable from that host, and having their response consumed as workflow binary/config data.

### Likelihood Explanation
Requires: (1) the node operator to have configured the file/HTTP-URL fetcher path (`Opts.FetcherFunc` override / `NewFetcherFunc`) instead of the default gateway-routed `FetcherService`, and (2) an unprivileged actor able to register a workflow with an attacker-controlled `BinaryURL`/`ConfigURL`. Given that the code comment in `newFileFetcher` explicitly acknowledges "Confidential workflows register with HTTP URLs (for the enclave)", this path is a real, intended production usage, not solely a test scaffold — but I could not fully confirm from the index which deployment configurations wire `Opts.FetcherFunc` to `NewFetcherFunc` versus the default `syncerV2.NewFetcherService` gateway path in production. This uncertainty affects overall exploitability/likelihood and would need verification in a full checkout.

### Recommendation
In `newHTTPFetcher`, after computing `fetchURL`/`u.Path`, add an explicit containment check analogous to the one already used in `newFileFetcher` (line 229): verify that the resolved path is either equal to, or has the original base path plus a path-separator as a prefix, and reject the request otherwise. Do not rely on `filepath.Clean`/`filepath.Join` alone to neutralize `..` sequences in user-controlled relative paths, since leading `..` segments in a relative path are not eliminated by `Clean` and can walk outside the intended base directory once joined.

### Proof of Concept
1. Operator configures the workflow registry syncer with a restrictive HTTP `baseURL`, e.g. `https://storage.internal.example.com/artifacts/tenantA/` (via `NewFetcherFunc`/`newHTTPFetcher`).
2. An unprivileged actor registers a workflow on the Workflow Registry contract with:
   `BinaryURL = "../../tenantB/secret-binary.wasm"`
3. `createWorkflowSpec` → `FetchWorkflowArtifacts` → `h.fetchFn` invokes `newHTTPFetcher`'s closure with `req.URL = "../../tenantB/secret-binary.wasm"`.
4. `cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")` yields `"../../tenantB/secret-binary.wasm"` (leading `..` not resolvable by `Clean`).
5. `u.Path = filepath.Join("/artifacts/tenantA", "../../tenantB/secret-binary.wasm")` resolves (via `Clean`) to `"/tenantB/secret-binary.wasm"`, escaping the intended `/artifacts/tenantA/` prefix — with no subsequent containment check before the request is issued.

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

**File:** core/services/workflows/syncer/v2/handler.go (L796-799)
```go

	// With Workflow Registry contract v2 the BinaryURL and ConfigURL are expected to be identifiers that put through the Storage Service.
	decodedBinary, config, err := h.workflowArtifactsStore.FetchWorkflowArtifacts(ctx, wfID, payload.BinaryURL, payload.ConfigURL)
	if err != nil {
```

**File:** core/services/workflows/artifacts/v2/store.go (L163-183)
```go
	// Fetch the binary files from the specified URLs.
	var (
		binary, decodedBinary, config []byte
	)

	maxBinarySize, err := h.limiters.MaxBinarySize.Limit(ctx)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get binary size limit: %w", err)
	} else if maxBinarySize < 0 {
		maxBinarySize = 0
	}
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
