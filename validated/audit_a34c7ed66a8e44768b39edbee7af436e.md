## Finding: Path traversal in `newHTTPFetcher` allows escaping the configured base URL path

The Sprockets bug (CVE‑2018‑3760) is a classic "insufficient normalization before path-prefix check" traversal that lets a client read resources outside an intended base directory. The Chainlink codebase has a directly analogous bug in the workflow artifact fetcher used for CRE/workflow binary & config retrieval.

### Root cause

`core/services/workflows/syncer/v2/fetcher.go` provides two fetcher implementations selected by `NewFetcherFunc` based on the scheme of a configured `baseURL`: [1](#0-0) 

For `file://` schemes, `newFileFetcher` correctly rejects paths that escape `basePath` by comparing the joined/cleaned path against `basePath+separator`: [2](#0-1) 

For `http`/`https` schemes, however, `newHTTPFetcher` only cleans the attacker-controlled `req.URL` component in isolation and then blindly joins it onto the configured base path with `filepath.Join`, **without validating that the resulting path stays within the base path**: [3](#0-2) 

Because `filepath.Join` collapses `..` segments across the whole joined string, a `req.URL` value like `../../other-tenant/secret.bin` will cause `u.Path` to resolve outside the intended base path (e.g., `https://storage.example.com/workflows` + `../../other-tenant/secret.bin` → `https://storage.example.com/other-tenant/secret.bin`), exactly the class of bug fixed in Sprockets (public-facing path traversal due to insufficient root confinement).

### Reachability

`req.URL` in this path is the workflow's `binaryURL`/`configURL`, taken directly from the on-chain Workflow Registry entry and passed unmodified into the fetch pipeline: [4](#0-3) 

`NewFetcherFunc` is wired in when a node operator configures `CRE().WorkflowFetcher().URL()`, and this fetcher **overrides and bypasses the DON/gateway consensus fetch path** entirely: [5](#0-4) [6](#0-5) 

Since `binaryURL`/`configURL` originate from workflow registrations (attacker/workflow-owner controlled data), and are fed straight into `newHTTPFetcher` without a "stay within basePath" check (unlike the `file://` variant which explicitly has one, and unlike other traversal-safe code in the repo such as `deployment/ccip/changeset/ccip-attestation-solana/cs_deploy_signer_registry_solana.go` which explicitly rejects `..`), a malicious workflow registration can cause the node to fetch (and subsequently trust as workflow binary/config content) arbitrary paths on the configured artifact-storage host — an information disclosure / SSRF-style path-traversal analogous to the Sprockets advisory.

### Title
Path traversal in workflow artifact HTTP fetcher via unvalidated `filepath.Join` on attacker-controlled URL - (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
`newHTTPFetcher` in `core/services/workflows/syncer/v2/fetcher.go` builds a fetch URL by joining a configured `baseURL` path with an unsanitized-relative-to-base `req.URL` (sourced from the on-chain workflow registry's `binaryURL`/`configURL`). Unlike the sibling `newFileFetcher`, it never verifies that the resulting path remains within the configured base path, allowing `..` traversal to reach arbitrary paths on the same host.

### Finding Description
`newHTTPFetcher` only calls `filepath.Clean` on the raw `req.URL` and joins it with `u.Path` via `filepath.Join`, which resolves `..` sequences across the full combined string — there is no post-join containment check comparable to the prefix check performed in `newFileFetcher` (`core/services/workflows/syncer/v2/fetcher.go:229`). A crafted `binaryURL`/`configURL` value containing `../` sequences can therefore cause the fetch request to target a path outside the operator-intended base path on the configured artifact-storage host.

### Impact Explanation
If a node operator configures `CRE.WorkflowFetcher.URL` (an `http`/`https` base URL) to bypass the gateway-based fetch, any workflow registered on-chain (which supplies `binaryURL`/`configURL`) can cause the node to fetch content from arbitrary paths on that host — potentially disclosing other tenants'/workflows' artifacts or internal endpoints co-located on the same storage host, and feeding attacker-influenced content into the node's workflow execution pipeline as "trusted" binary/config data. This matches CWE-22/CWE-200 impact (unauthorized information disclosure via path traversal) from the referenced advisory.

### Likelihood Explanation
Requires the node operator to have configured the direct HTTP `WorkflowFetcher` bypass (rather than the default gateway/DON consensus path) — this is an operator opt-in configuration, but once enabled, the `binaryURL`/`configURL` values are attacker (workflow-registrant) controlled, making exploitation straightforward for any actor able to register a workflow.

### Recommendation
In `newHTTPFetcher`, after joining `cleanPath` onto the base URL, verify the resulting path is still prefixed by the original base path (mirroring the `basePath+separator` check already used in `newFileFetcher`), and reject the request otherwise.

### Proof of Concept
1. Configure `CRE.WorkflowFetcher.URL = https://storage.example.com/workflows`.
2. Register a workflow whose `binaryURL` is `../../other-tenant/secret.bin` (or an absolute-looking traversal string).
3. `newHTTPFetcher` computes `u.Path = filepath.Join("/workflows", "../../other-tenant/secret.bin")`, which resolves to `/other-tenant/secret.bin`, causing the node to fetch and process content from outside the intended `/workflows` base path. [7](#0-6)

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
