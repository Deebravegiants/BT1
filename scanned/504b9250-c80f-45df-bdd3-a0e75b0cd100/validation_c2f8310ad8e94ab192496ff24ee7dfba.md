### Title
Path Traversal via Unvalidated `req.URL` in `newHTTPFetcher` Allows Escaping the Configured Base URL Path - (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds an outbound HTTP request URL by joining a fixed `baseURL` with an attacker-influenced `req.URL` (the workflow's `BinaryURL`/`ConfigURL`), applying `filepath.Clean` + `TrimPrefix("/")` but never verifying that the final joined path stays within the intended base path — the same missing "post-join normalization check" root cause described in the Traefik `ReplacePathRegex` advisory.

### Finding Description
`newHTTPFetcher` performs path construction like this: [1](#0-0) 

```go
cleanPath := strings.TrimPrefix(filepath.Clean(req.URL), "/")
...
u.Path = filepath.Join(u.Path, cleanPath)
```

`filepath.Clean` on a *relative* path that begins with `..` does **not** strip the leading `..` segments (it only collapses redundant separators/dot-segments while preserving leading traversal, unlike its behavior on absolute paths). Because `TrimPrefix(..., "/")` only removes a leading slash and does nothing for a value like `../../secret`, `cleanPath` can still contain unresolved `..` sequences. `filepath.Join(u.Path, cleanPath)` then re-cleans the combined string, which can walk `cleanPath`'s `..` segments past `u.Path` entirely, producing a URL path outside the directory that `baseURL` was meant to constrain.

This mirrors the CVE-2026-65600 root cause exactly: a normalize-then-forward pattern where the check happens *before* structural composition (`Join`) rather than validating the *final* composed value against its normalized form. Compare this to the sibling function `newFileFetcher` in the same file, which correctly performs the join first and only *then* validates the result is still prefixed by `basePath`: [2](#0-1) 

`newHTTPFetcher` has no equivalent post-join containment check.

The `req.URL` value that reaches this function originates from `BinaryURL`/`ConfigURL` fields of on-chain `WorkflowRegisteredEvent` / `WorkflowActivatedEvent` payloads, which are supplied by the workflow owner when registering a workflow, and flow through `Store.FetchWorkflowArtifacts` unmodified into `ghcapabilities.Request{URL: binaryURL/configURL}`: [3](#0-2) [4](#0-3) 

### Impact Explanation
An unprivileged workflow owner registering a workflow controls `BinaryURL`/`ConfigURL` and can supply a path containing `../` segments. If the node is configured with `NewFetcherFunc` pointed at an `http(s)://` base (used to "bypass the gateway" per the code comment at `core/services/workflows/syncer/v2/fetcher.go:172-173`), a crafted URL can cause the node to fetch content from a path outside the intended base directory on that host — potentially reaching resources not meant to be exposed to workflow artifact fetching (e.g., other tenants' artifacts, internal-only paths on the same host). This is a lower-severity analog of the Traefik bug (no authentication middleware is bypassed here, since this fetcher path is a direct HTTP client, not a proxy protecting routes with auth), but it is a genuine path-confinement/traversal defect reachable from unprivileged, attacker-supplied workflow metadata.

### Likelihood Explanation
Reachability requires (a) the node configured to use the HTTP variant of `NewFetcherFunc` (as opposed to the storage-service-backed default fetch path), and (b) the target host to expose sensitive content at paths reachable by traversal from the configured base path. Given `newFileFetcher`'s explicit traversal-prevention test coverage (`fetcher_test.go`) contrasts with the complete absence of equivalent tests/checks for `newHTTPFetcher`, this looks like an overlooked case rather than a mitigated one, but the effective blast radius depends on gateway/host-side configuration not fully visible in this codebase and cannot be confirmed as exploitable "authentication bypass" per the advisory's original definition.

### Recommendation
Add a post-`Join` containment check in `newHTTPFetcher`, analogous to the fix pattern already used in `newFileFetcher`: after computing `u.Path = filepath.Join(u.Path, cleanPath)`, verify the resulting path still has the original base path as prefix (or reject any `req.URL` whose cleaned value still contains leading `..` after trimming), returning an error instead of proceeding with the outbound request.

### Proof of Concept
1. Configure `NewFetcherFunc("http://artifacts.example.com/tenantA", lggr)`.
2. Register a workflow with `BinaryURL = "../tenantB/secret.wasm"` (or equivalent `../../` sequence).
3. `newHTTPFetcher`'s `cleanPath` remains `"../tenantB/secret.wasm"` after `filepath.Clean`+`TrimPrefix("/")` (no leading slash to strip).
4. `u.Path = filepath.Join("/tenantA", "../tenantB/secret.wasm")` resolves to `/tenantB/secret.wasm` — outside the intended `/tenantA` base — and the node issues the fetch to that unintended path.

*Note: I could not fully confirm from the indexed code whether any production deployment actually configures the `http(s)` scheme for `NewFetcherFunc` (versus the storage-service/gateway-backed default path), which limits certainty on real-world exploitability. A Devin session with full repository/config access would be needed to verify deployment usage.*

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

**File:** core/services/workflows/artifacts/v2/store.go (L217-224)
```go
		req := ghcapabilities.Request{
			URL:              configURL,
			Method:           http.MethodGet,
			MaxResponseBytes: safeUint32(uint64(maxResponseBytes)),
			WorkflowID:       workflowID,
		}

		config, err2 = h.fetchFn(ctx, messageID(configURL, workflowID), req)
```
