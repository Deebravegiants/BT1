Based on the analysis, the claim is well-supported by the code. Confirmed findings:

1. `NewFetcherFunc`'s HTTP branch (`newHTTPFetcher`) lacks the base-path containment check that `newFileFetcher` has [1](#0-0)  vs [2](#0-1) .

2. This is wired into production: `core/cmd/shell.go` sets `creOpts.FetcherFunc` from `cfg.CRE().WorkflowFetcher().URL()` via `NewFetcherFunc` when that config value is set [3](#0-2) , and `newFetcherServiceV2` in `core/services/cre/cre.go` uses `opts.FetcherFunc` directly (bypassing the gateway-routed `FetcherService.Fetch`) whenever it is non-nil [4](#0-3) .

3. The workflow-owner-supplied `BinaryURL`/`ConfigURL` flow directly into `req.URL` for `fetchFn` unless the host matches `ArtifactStorageHost` (which triggers a signed-URL swap instead) [5](#0-4) [6](#0-5) .

4. The existing test suite explicitly validates the containment check for the file fetcher (`"../../../etc/passwd"` rejected) but there is no equivalent traversal-rejection test for the HTTP fetcher [7](#0-6) , confirming the asymmetry.

This satisfies the required validation checks: exact file/function/line references, clear root cause (missing prefix-containment check that exists in the sibling `newFileFetcher` implementation), a reachable exploit path from an unprivileged workflow-registering actor, and a concrete impact (fetching content from unintended paths on the configured storage host, i.e., cross-tenant/cross-workflow artifact disclosure).

Audit Report

## Title
Directory traversal in HTTP artifact fetcher bypasses intended base-path restriction - (File: core/services/workflows/syncer/v2/fetcher.go)

## Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds the outbound artifact-fetch URL by joining a workflow-owner-supplied path onto a configured base URL using `filepath.Join`, without verifying the resulting path stays within the intended base path — unlike the sibling `newFileFetcher`, which explicitly performs this containment check. When the node is configured with `CRE.WorkflowFetcher.URL` set to an `http(s)` URL, a workflow owner can supply a `BinaryURL`/`ConfigURL` containing `../` sequences to escape the configured base path on the target storage host.

## Finding Description
`NewFetcherFunc` dispatches on scheme to either `newFileFetcher` (file://) or `newHTTPFetcher` (http/https) [8](#0-7) . `newFileFetcher` cleans the incoming path and explicitly rejects it unless it is prefixed by `basePath` [1](#0-0) . `newHTTPFetcher` only does `filepath.Clean` on the raw request URL and joins it onto the base URL's path via `filepath.Join`, with no equivalent post-join containment check [2](#0-1) . Because `filepath.Join` invokes `Clean`, a crafted path with enough `../` segments collapses the base path and lands on an unintended sibling path on the same host.

This fetcher is reachable with workflow-owner-controlled input: `Store.FetchWorkflowArtifacts` passes `binaryURL`/`configURL` (registered on-chain via the Workflow Registry) straight to `h.fetchFn` unless the URL's host matches the configured `ArtifactStorageHost`, in which case a signed URL is substituted instead [5](#0-4) [6](#0-5) . `h.fetchFn` is `NewFetcherFunc`'s output when the node operator configures `CRE.WorkflowFetcher.URL`, which is wired in at `core/cmd/shell.go` and takes precedence over the gateway-routed fetcher in `newFetcherServiceV2` [3](#0-2) [4](#0-3) .

The existing test suite confirms the file-fetcher path-traversal case is explicitly rejected [7](#0-6) , but no equivalent check or test exists for `newHTTPFetcher`.

## Impact Explanation
When `CRE.WorkflowFetcher.URL` is configured with an http(s) base URL pointing to a subdirectory (e.g. `https://storage.example.com/artifacts/`), a workflow owner supplying a `ConfigURL`/`BinaryURL` whose host does not match `ArtifactStorageHost` (so no signed-URL substitution occurs) can craft a path such as `../../secrets/other-config.yaml`. `filepath.Join` collapses this against the base path, causing the node to fetch content outside the intended `/artifacts/` prefix on the configured host — a concrete cross-tenant/cross-workflow artifact disclosure, mirroring the CVE-2016-10039 bug class. This falls under the "cross-user response confusion"/allowlist-bypass impact category.

## Likelihood Explanation
The exploit requires only that an unprivileged actor register a workflow on-chain with a crafted `BinaryURL`/`ConfigURL` — no elevated privileges are needed. The precondition is that the node operator has configured `CRE.WorkflowFetcher.URL` with an http/https base URL (a legitimate, supported configuration option per `core/config/toml/types.go` and `docs/CONFIG.md`), rather than relying exclusively on the gateway-routed `FetcherService.Fetch`. Given this is a documented configuration knob wired directly in `core/cmd/shell.go`, the likelihood is realistic, not purely hypothetical.

## Recommendation
In `newHTTPFetcher`, after computing `u.Path = filepath.Join(u.Path, cleanPath)`, verify that the resulting path is still prefixed by the original base URL's path (or exactly equal to it), mirroring the check already present in `newFileFetcher`, and reject the request otherwise.

## Proof of Concept
1. Configure `CRE.WorkflowFetcher.URL = "https://storage.example.com/artifacts"`.
2. Register a workflow with `ConfigURL = "https://storage.example.com/../../secrets/other-config.yaml"` (host differs from or does not trigger the `ArtifactStorageHost` signed-URL swap, or `ArtifactStorageHost` retrieval is not configured).
3. Add a unit test analogous to the existing file-fetcher traversal test in `core/services/workflows/syncer/v2/fetcher_test.go` (lines 443-448), but targeting `newHTTPFetcher`/`NewFetcherFunc` with an `http://` base URL and a request `URL: "../../../secret/config"`, asserting the resulting `fetchURL` stays within the base path (it currently does not, and no error is raised).

### Citations

**File:** core/services/workflows/syncer/v2/fetcher.go (L184-196)
```go
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

**File:** core/cmd/shell.go (L300-305)
```go
	if cfg.CRE().WorkflowFetcher() != nil && cfg.CRE().WorkflowFetcher().URL() != "" {
		creOpts.FetcherFunc, err = syncerv2.NewFetcherFunc(cfg.CRE().WorkflowFetcher().URL(), appLggr)
		if err != nil {
			return nil, fmt.Errorf("failed to create workflow fetcher: %w", err)
		}
	}
```

**File:** core/services/cre/cre.go (L813-815)
```go
	if opts.FetcherFunc != nil {
		return opts.FetcherFunc, nil, []commonsrv.Service{}, nil
	}
```

**File:** core/services/workflows/artifacts/v2/store.go (L149-161)
```go
	// If the binary URL points to the artifact storage host, use the retrieve function to get the signed URL.
	// NOTE: retrieveFunc may be nil if the fetcherFunc was overridden.
	// TODO CRE-632: retrieverFunc should enforced made to always be set, once local CRE can support it.
	if h.retrieveFunc != nil && parsedBinaryURL.Host == h.config.ArtifactStorageHost {
		signedBinaryURL, err2 := h.retrieveFunc(ctx, &storage_service.DownloadArtifactRequest{
			Id:   workflowID,
			Type: storage_service.ArtifactType_ARTIFACT_TYPE_BINARY,
		})
		if err2 != nil {
			return nil, nil, fmt.Errorf("failed to get binary artifact URL: %w", err2)
		}
		binaryURL = signedBinaryURL
	}
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

**File:** core/services/workflows/syncer/v2/fetcher_test.go (L443-448)
```go
		// Test path traversal attempt
		_, err = fetcher(ctx, "test-msg-id", ghcapabilities.Request{
			URL: "../../../etc/passwd",
		})
		require.Error(t, err)
		assert.Contains(t, err.Error(), "is not within the basePath")
```
