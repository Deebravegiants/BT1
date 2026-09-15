This is a valid finding. The test confirms the intended usage: `req.URL` in `newHTTPFetcher` is expected to be a *relative* path (e.g. `"test.json"`) that gets joined onto the configured `baseURL`, exactly the same usage pattern that `newFileFetcher` protects with a post-join containment check. The tests demonstrate this relative-path model works (`http fetcher` test case), and separately demonstrate that `newFileFetcher` explicitly rejects `"../../../etc/passwd"` with "is not within the basePath" — but no equivalent test or check exists for `newHTTPFetcher`, confirming the asymmetry described in the claim.

Audit Report

## Title
Missing containment check allows path traversal in workflow artifact HTTP fetcher - (File: core/services/workflows/syncer/v2/fetcher.go)

## Summary
`newHTTPFetcher` builds the outbound fetch URL by cleaning `req.URL` and joining it onto `baseURL` with `filepath.Join`, without any post-join verification that the result stays within the configured base path. Its sibling `newFileFetcher` in the same file performs exactly this containment check, showing the omission is an inconsistency rather than intended behavior.

## Finding Description
`newFileFetcher` cleans and joins the request path, then explicitly validates containment: `strings.HasPrefix(fullPath, basePath+string(filepath.Separator))`, rejecting anything outside `basePath` [1](#0-0) . `newHTTPFetcher` only does `cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")` and `u.Path = filepath.Join(u.Path, cleanPath)`, then issues the request with no equivalent check [2](#0-1) . `filepath.Clean("../../secret")` preserves leading `..` segments, and `filepath.Join(basePath, "../../secret")` walks outside `basePath`, so a relative `req.URL` containing `../` sequences escapes the intended base path on the configured host.

`req.URL` is populated from workflow-registry-supplied `binaryURL`/`configURL` in `FetchWorkflowArtifacts` [3](#0-2) , which originate from workflow registration data controlled by whoever registers a workflow. `newHTTPFetcher` is only reached via `NewFetcherFunc` when `opts.FetcherFunc` is supplied, which bypasses the gateway's SSRF-hardened `FetcherService.Fetch` path entirely [4](#0-3) [5](#0-4) .

## Impact Explanation
Where this fetcher mode is configured (an operator-selected deployment option, not the default gateway-mediated path), an unprivileged workflow author who can register a `BinaryURL`/`ConfigURL` can craft a relative path with `../` segments to make the fetcher issue requests outside the operator-intended base path on the configured host — a confused-deputy/path-traversal read of unintended resources on that host. This breaks the "read only within the configured base path" invariant that the codebase clearly intends to enforce, evidenced by the containment check present in `newFileFetcher`. Impact is bounded to the same host/scheme (no host/port pivot), and only affects deployments that explicitly configure `opts.FetcherFunc` with an `http`/`https` base URL instead of the standard gateway `FetcherService`.

## Likelihood Explanation
Likelihood depends on this non-default configuration being in use. When it is, any actor able to register a workflow (an otherwise unprivileged action, gated only by normal workflow-registration mechanics) can trigger the escape with a single crafted relative URL containing `../` sequences — no special privilege beyond workflow registration is required, and it is trivially repeatable.

## Recommendation
Add a post-join containment check in `newHTTPFetcher` mirroring the one in `newFileFetcher`: after computing the joined path, verify it remains prefixed by the base path (or reject `req.URL` values containing `..` components outright) before constructing `fetchURL`, and return an error analogous to `"is not within the basePath"` when the check fails.

## Proof of Concept
1. Configure `NewFetcherFunc` with `baseURL = "https://artifacts.example.com/served-root"` (i.e., set `opts.FetcherFunc` accordingly).
2. Invoke the resulting `FetcherFunc` (as `Store.FetchWorkflowArtifacts` would) with `req.URL = "../../secret-config"`.
3. `cleanPath` remains `"../../secret-config"` after `filepath.Clean`/`TrimPrefix`.
4. `u.Path = filepath.Join("/served-root", "../../secret-config")` resolves to `/secret-config`.
5. The outbound GET is sent to `https://artifacts.example.com/secret-config`, outside `/served-root`, with no containment check blocking it — contrast with `newFileFetcher`, which would reject the equivalent traversal attempt with `"is not within the basePath"` (as shown in the existing test `fetcher_test.go`'s "Test path traversal attempt" case, which has no HTTP-fetcher equivalent).

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

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-261)
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

		lggr.Debugw("Fetching HTTP resource", "url", fetchURL, "workflowID", req.WorkflowID)
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

**File:** core/services/cre/cre.go (L807-815)
```go
func newFetcherServiceV2(
	opts Opts,
	capCfg config.Capabilities,
	lggr logger.Logger,
	gatewayConnectorWrapper *gatewayconnector.ServiceWrapper,
) (wftypes.FetcherFunc, wftypes.LocationRetrieverFunc, []commonsrv.Service, error) {
	if opts.FetcherFunc != nil {
		return opts.FetcherFunc, nil, []commonsrv.Service{}, nil
	}
```
