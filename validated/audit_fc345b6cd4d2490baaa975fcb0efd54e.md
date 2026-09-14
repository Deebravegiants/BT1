### Title
Path traversal in workflow artifact HTTP fetcher via unvalidated URL join - (File: core/services/workflows/syncer/v2/fetcher.go)

### Summary
The Mail gem advisory (CVE-2012-2139) describes a directory-traversal bug where a user-controlled path parameter is concatenated into a filesystem/URL path without proper containment checks, letting an attacker read files outside the intended directory. An analogous pattern exists in the alternate (non-gateway) workflow artifact fetcher used by chainlink, specifically `newHTTPFetcher`, where an attacker-influenced `req.URL` is joined onto a configured base path without verifying the result stays within that base.

### Finding Description
`newFetcherFunc`/`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds an outbound request URL by cleaning and joining the caller-supplied `req.URL` onto the configured base URL's path: [1](#0-0) 

```go
func newHTTPFetcher(baseURL string, lggr logger.Logger) types.FetcherFunc {
    ...
    return func(ctx context.Context, messageID string, req ghcapabilities.Request) ([]byte, error) {
        cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")
        u, err := url.Parse(baseURL)
        ...
        u.Path = filepath.Join(u.Path, cleanPath)
        fetchURL := u.String()
        ...
    }
}
```

Unlike the sibling `newFileFetcher` implementation in the same file, which explicitly validates that the resolved path stays within `basePath` (`strings.HasPrefix(fullPath, basePath+string(filepath.Separator))`) before reading, `newHTTPFetcher` performs no such containment check after the `filepath.Join`. Because `filepath.Clean` does not collapse a relative leading `../` sequence, and `filepath.Join(u.Path, cleanPath)` will happily walk `cleanPath`'s `..` segments upward past `u.Path`, a `req.URL` value such as `../../secret-path` can cause the constructed request URL to escape the intended base path segment on the configured artifact host.

This is reachable from an unprivileged, external actor: `req.URL` originates as the `BinaryURL`/`ConfigURL` fields of an on-chain `WorkflowRegisteredEvent`, which any workflow owner can set when registering a workflow. These values flow, unsanitized for traversal, into `Store.FetchWorkflowArtifacts`: [2](#0-1) 

and ultimately into the configured `fetchFn`. When the node operator configures `CRE().WorkflowFetcher().URL()` as an `http(s)://` base (an officially supported configuration path per `NewFetcherFunc`/`NewApplication` wiring in `core/cmd/shell.go`), that fetcher becomes `opts.FetcherFunc`, bypassing the gateway broker entirely and directly using `newHTTPFetcher` with attacker-supplied `req.URL`.

### Impact Explanation
An unprivileged workflow owner who registers a workflow with a maliciously crafted `BinaryURL`/`ConfigURL` (containing `../` sequences) can cause the node to issue HTTP(S) requests to paths on the configured artifact host outside the intended base directory/prefix. Depending on how the artifact-storage backend is structured, this can expose artifacts, configuration, or internal endpoints not meant to be reachable through this proxy path — a request-path confusion / traversal analogous to the Mail gem's file-delivery traversal. Because the node then parses and executes the fetched "artifact" as workflow binary/config, this could also enable fetching of unintended/unauthorized data disguised as legitimate workflow content.

### Likelihood Explanation
Exploitability requires the node operator to have configured the HTTP-based standalone fetcher (`CRE().WorkflowFetcher().URL()` with an `http`/`https` scheme) instead of relying on the gateway-mediated `FetcherService.Fetch` path. This is a supported, documented configuration surface (used e.g. for local/dev artifact hosting), and once enabled, the only precondition for exploitation is registering a workflow on-chain with a crafted URL — an action available to any unprivileged workflow owner, requiring no special node access.

### Recommendation
Apply the same containment validation used in `newFileFetcher` to `newHTTPFetcher`: after constructing `u.Path = filepath.Join(u.Path, cleanPath)`, verify the resulting path still has the original base path as a prefix (with a path-separator boundary) before issuing the request, and reject the request otherwise. Consider centralizing the traversal-safe join logic so both fetchers share a single vetted implementation.

### Proof of Concept
1. Configure the node with `CRE.WorkflowFetcher.URL = "http://artifact-host/artifacts"`.
2. As an unprivileged actor, register a workflow on-chain with `BinaryURL = "http://artifact-host/artifacts/../internal/secret.wasm"` (or equivalently a relative value that, once cleaned/joined, escapes `/artifacts`).
3. When the node syncs the workflow, `Store.FetchWorkflowArtifacts` invokes `fetchFn` with this URL; `newHTTPFetcher` computes `cleanPath = "../internal/secret.wasm"` and joins it onto `u.Path` (`/artifacts`), producing `u.Path = "/internal/secret.wasm"` — outside the intended `/artifacts` directory — and issues the GET request there, unlike `newFileFetcher` which would reject the equivalent traversal attempt.

### Citations

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

**File:** core/services/workflows/artifacts/v2/store.go (L174-182)
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
```
