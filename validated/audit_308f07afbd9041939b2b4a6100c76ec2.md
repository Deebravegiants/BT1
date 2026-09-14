### Title
Missing containment check allows path traversal / SSRF-style URL escape in workflow artifact HTTP fetcher - (File: core/services/workflows/syncer/v2/fetcher.go)

### Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds the outgoing fetch URL by cleaning the attacker-influenced `req.URL` path and joining it onto the configured `baseURL` path with `filepath.Join`, but — unlike its sibling `newFileFetcher` in the same file — it never verifies that the resulting joined path is still contained within the base path. This mirrors the rclone `serve restic` `WithRemote` root-escape flaw: cleaning/validating a path *before* join instead of checking containment *after* join allows a leading `../` (or several) to walk the resulting request outside the intended base directory.

### Finding Description
`newFileFetcher` correctly performs a post-join containment check: [1](#0-0) 

`newHTTPFetcher`, which handles the `http`/`https` scheme branch of `NewFetcherFunc`, only cleans the path and joins it — it has no equivalent containment check before issuing the outbound HTTP request: [2](#0-1) 

`filepath.Clean("../../secret")` preserves leading `..` components (same property exploited in the rclone advisory), and `filepath.Join(basePath, "../../secret")` will walk up and out of `basePath`, changing `u.Path` to point at a sibling/parent path on the same configured host. Because there is no `strings.HasPrefix(resultingPath, basePath)` check analogous to the one in `newFileFetcher`, the outbound request silently escapes the operator-intended base path.

`req.URL` originates from `ghcapabilities.Request.URL`, which is populated from `BinaryURL`/`ConfigURL` values stored in the on-chain/off-chain Workflow Registry entry supplied at workflow-registration time (`core/services/workflows/artifacts/v2/store.go`, `FetchWorkflowArtifacts`), i.e. attacker-influenced input from whoever can register a workflow: [3](#0-2) 

`NewFetcherFunc` (and therefore `newHTTPFetcher`) is only wired in when `opts.FetcherFunc` is explicitly supplied to `newFetcherServiceV2`, bypassing the normal gateway-mediated `FetcherService.Fetch` path (which itself goes through the SSRF-hardened `httpclient.go` with `safeurl` allow-listing): [4](#0-3) 

The comment on `NewFetcherFunc` explicitly states it "bypasses the gateway," meaning none of the gateway's IP/port/scheme allow-listing (`core/services/gateway/network/httpclient.go`) applies to requests issued through `newHTTPFetcher`.

### Impact Explanation
When this fetcher is configured, a workflow author (an otherwise unprivileged, non-operator actor able to register `BinaryURL`/`ConfigURL` on the workflow registry) can craft a URL whose path component contains leading `../` sequences. The resulting request path escapes the operator-configured base URL path, allowing:
- Reading artifacts/resources at other paths on the same configured host outside the intended base directory (confused-deputy / cross-tenant read).
- Because it bypasses the gateway's outbound `safeurl`-based SSRF protections, an attacker could reach a broader path surface than the operator intended, similar in spirit to the rclone advisory's backend root escape.

The severity is somewhat bounded because the escape is limited to path traversal on the same host/scheme (no IP/port pivot since the host portion of `baseURL` is fixed), but it still breaks the "read/write only within the configured base path" security boundary the code clearly intends to enforce (as evidenced by the containment check present in the sibling `newFileFetcher`).

### Likelihood Explanation
Likelihood is limited by deployment configuration: `newHTTPFetcher` is only reached when `opts.FetcherFunc` (an `http`/`https` `baseURL`) is configured instead of the standard gateway-backed `FetcherService`. Where this configuration is used, any workflow owner able to register a workflow with an artifact URL can trigger the flaw with a single crafted URL — no special privilege beyond ordinary workflow registration is required, making it easy to trigger once reachable.

### Recommendation
Add the same post-join containment check used in `newFileFetcher` to `newHTTPFetcher`: after computing `u.Path = filepath.Join(u.Path, cleanPath)`, verify that the resulting path still has the original base path as a prefix (or use `net/url`-safe joining plus an explicit `..`/`.` component rejection, e.g. via `io/fs.ValidPath`-style validation of `cleanPath`) before constructing `fetchURL`. Reject the request with an error if the check fails, mirroring the `is not within the basePath` error used in `newFileFetcher`.

### Proof of Concept
1. Configure `NewFetcherFunc` with `baseURL = "https://artifacts.example.com/served-root"`.
2. Register a workflow (or otherwise trigger `Store.FetchWorkflowArtifacts`) with `BinaryURL` (or `ConfigURL`) set to a relative path such as `"../../secret-config"`.
3. In `newHTTPFetcher`, `cleanPath := strings.TrimPrefix(filepath.Clean("../../secret-config"), "/")` yields `"../../secret-config"` unchanged (leading `..` preserved by `filepath.Clean`, as in the rclone bug).
4. `u.Path = filepath.Join("/served-root", "../../secret-config")` resolves to `/secret-config`, escaping `/served-root` entirely.
5. The outbound GET request is sent to `https://artifacts.example.com/secret-config` with no containment check, unlike the equivalent `newFileFetcher` path, exfiltrating data outside the intended served-root.

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
