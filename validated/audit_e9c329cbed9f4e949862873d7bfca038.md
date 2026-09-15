Based on my investigation, the strongest analog to the `arrayfire-js` HTTP-download-executable advisory in this codebase is the CRE workflow artifact fetching path, where the DON's own HTTP client allows plain `http://` by default (`defaultAllowedSchemes = []string{"http", "https"}`), and this scheme is actually used to fetch and then execute a WASM workflow binary.

### Title
Workflow binary/config artifacts may be fetched and executed over unauthenticated plain HTTP - ([File: core/services/workflows/artifacts/v2/store.go], [File: core/services/gateway/network/httpclient.go])

### Summary
`Store.FetchWorkflowArtifacts` [1](#0-0)  downloads the workflow binary and config from a `binaryURL`/`configURL` that is supplied on-chain by the workflow owner via the `WorkflowRegistryV2` contract (`UpsertWorkflow`), without ever validating that the scheme is `https`. The actual fetch is performed by the gateway's HTTP client, whose default `AllowedSchemes` explicitly includes plain `"http"` alongside `"https"` [2](#0-1) . This mirrors the `arrayfire-js` bug class (CVE-2016-10598): an executable payload — here a WASM workflow binary that the node will decode and run — is fetched over an unauthenticated channel that a network-privileged attacker (or a compromised/complicit HTTP endpoint on the path) can tamper with.

### Finding Description
1. A workflow owner (an unprivileged, permissionless on-chain actor once linked/allowlisted) registers a workflow via `UserWorkflowUpsert`/`UpsertWorkflow`, supplying an arbitrary `BinaryURL` and `ConfigURL` [3](#0-2) . There is no validation anywhere in this path that `BinaryURL`/`ConfigURL` must use `https`.
2. When the DON observes the `WorkflowRegisteredEvent`, `FetchWorkflowArtifacts` parses the URL and, unless it matches the trusted `ArtifactStorageHost` (in which case a signed URL is fetched instead), passes the raw `binaryURL`/`configURL` straight to `h.fetchFn` as an `ghcapabilities.Request` [4](#0-3) . No scheme check (`https`-only) is performed on the caller-supplied URL before it is fetched.
3. That fetch is executed by the gateway's outbound HTTP action/client (`core/services/gateway/network/httpclient.go`), whose defaults explicitly permit the `http` scheme (`defaultAllowedSchemes = []string{"http", "https"}`) unless an operator overrides the gateway job config to restrict to `https` only [2](#0-1) . Some gateway job templates (`GatewayJob.Resolve`) do default `AllowedSchemes` to `["https"]` [5](#0-4) , but the underlying `httpclient.go` package-level default (used when no explicit gateway job template restriction is applied, e.g. via `NewHTTPClient`/`NewHTTPClientFactory` with a bare config) still allows `http`.
4. The fetched bytes are base64-decoded and passed directly to the workflow engine to be executed as the workflow's WASM binary [6](#0-5) . There's no integrity check (hash/signature) of the fetched binary against anything pinned on-chain — the `workflowID` itself is derived by hashing the binary/config content off-chain by the registering party, not verified against the downloaded bytes inside `FetchWorkflowArtifacts`.

Because `http://` is a permitted scheme end-to-end, a network-position attacker between the DON node and the artifact host (or a compromised/relaying CDN edge) can intercept the plaintext HTTP response and substitute a malicious WASM binary, which the node will then decode and execute inside the workflow engine — directly analogous to the `arrayfire-js` MITM-executable-substitution vulnerability.

### Impact Explanation
If exploited, an attacker with network MITM capability against a `http://` artifact URL registered by (or in collusion with) any workflow owner can cause every node in the DON that processes that workflow to execute an attacker-controlled WASM binary. Depending on the WASM engine's capability sandboxing, this can range from denial of service/crash to abuse of any capabilities granted to the workflow (HTTP egress, on-chain writes, secrets access) — i.e., unauthorized job run with attacker-controlled logic across the DON.

### Likelihood Explanation
Exploitation requires: (a) a workflow (owned by any linked/allowlisted address) registered with an `http://` binary/config URL instead of `https://`, and (b) an attacker able to intercept/tamper with that specific HTTP flow (on-path network position, e.g. rogue Wi-Fi, compromised router, ISP, or a malicious/compromised CDN edge serving the artifact). This is not trivially remote/unprivileged-attacker-only (it needs a MITM position), which is consistent with the original advisory's own caveat that exploitation requires a privileged network position. Likelihood is elevated by the fact that `http` is allowed by default in the shared HTTP client and is used in several non-test code comments/paths (e.g. `system-tests/lib/cre/workflow/workflow.go` explicitly notes "keep the HTTP URL on-chain; the enclave fetches the binary itself" [7](#0-6) ), suggesting `http://` artifact URLs are an accepted/expected configuration in some deployments, not merely a theoretical misconfiguration.

### Recommendation
Enforce `https`-only schemes for `binaryURL`/`configURL` at the point they are accepted, in two places:
1. Contract/changeset-level validation (`UserWorkflowUpsert.VerifyPreconditions` in `deployment/cre/workflow_registry/v2/changeset/user_workflow_registry.go`) should reject non-`https` (and non-trusted-storage-host) URLs before submission.
2. `Store.FetchWorkflowArtifacts` in `core/services/workflows/artifacts/v2/store.go` should validate `parsedBinaryURL.Scheme`/`parsedConfigURL.Scheme` and reject anything other than `https` (or the internal `ArtifactStorageHost` signed-URL flow) regardless of what the underlying gateway HTTP client's `AllowedSchemes` permits, so a misconfigured/default gateway client cannot silently downgrade this to plaintext HTTP. Additionally, consider requiring content-hash verification of the fetched binary/config against a value committed on-chain at registration time, independent of transport security.

### Proof of Concept
1. Workflow owner calls `UpsertWorkflow` on the `WorkflowRegistryV2` contract with `BinaryURL = "http://attacker-controlled-or-legit-host/binary"`.
2. DON node observes the event and calls `FetchWorkflowArtifacts`, which parses the URL, finds it doesn't match `ArtifactStorageHost`, and issues an `ghcapabilities.Request{URL: binaryURL, Method: GET}` [8](#0-7)  — no scheme check is performed.
3. If the outbound gateway HTTP client has not been explicitly locked to `https` (i.e., it's built with `AllowedSchemes` left at its default, per `httpclient.go` line 114), the request over plain HTTP succeeds.
4. An on-path attacker intercepts the HTTP response and substitutes a malicious base64-encoded WASM payload; the node decodes it and hands it to the workflow engine for execution as if it were the legitimate binary — reproducing the "attacker on the network path swaps an insecurely-downloaded executable" scenario from the CVE-2016-10598 advisory.

### Citations

**File:** core/services/workflows/artifacts/v2/store.go (L131-187)
```go
func (h *Store) FetchWorkflowArtifacts(ctx context.Context, workflowID, binaryURL, configURL string) ([]byte, []byte, error) {
	// Check if the workflow spec is already stored in the database.
	// A row whose binary payload is empty is a pause tombstone - don't use it.
	if spec, err := h.orm.GetWorkflowSpec(ctx, workflowID); err == nil && spec.Workflow != "" {
		// there is no update in the BinaryURL or ConfigURL, lets decode the stored artifacts
		decodedBinary, err := hex.DecodeString(spec.Workflow)
		if err != nil {
			return nil, nil, fmt.Errorf("failed to decode stored workflow spec: %w", err)
		}
		return decodedBinary, []byte(spec.Config), nil
	}

	// Determine which URL to retrieve workflow binary artifacts from
	parsedBinaryURL, err := url.Parse(binaryURL)
	if err != nil {
		return nil, nil, fmt.Errorf("invalid binary URL: %w", err)
	}

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

	if decodedBinary, err = base64.StdEncoding.DecodeString(string(binary)); err != nil {
		return nil, nil, fmt.Errorf("failed to decode binary: %w", err)
	}
```

**File:** core/services/gateway/network/httpclient.go (L112-114)
```go
var (
	defaultAllowedPorts   = []int{80, 443}
	defaultAllowedSchemes = []string{"http", "https"}
```

**File:** deployment/cre/workflow_registry/v2/changeset/user_workflow_registry.go (L62-76)
```go
func (u UserWorkflowUpsert) VerifyPreconditions(e cldf.Environment, config UserWorkflowUpsertInput) error {
	if err := validateWorkflowIDHex(config.WorkflowID); err != nil {
		return err
	}
	if config.WorkflowName == "" {
		return errors.New("workflow name cannot be empty")
	}
	if config.DonFamily == "" {
		return errors.New("DON family cannot be empty")
	}
	if config.BinaryURL == "" {
		return errors.New("binary URL cannot be empty")
	}
	return nil
}
```

**File:** deployment/cre/jobs/pkg/gateway_job.go (L185-196)
```go
	httpCfg := httpClientConfig{
		MaxResponseBytes: 50_000_000,
		AllowedPorts:     []int{443},
		AllowedSchemes:   []string{"https"},
	}

	if len(g.AllowedPorts) > 0 {
		httpCfg.AllowedPorts = g.AllowedPorts
	}
	if len(g.AllowedSchemes) > 0 {
		httpCfg.AllowedSchemes = g.AllowedSchemes
	}
```

**File:** system-tests/tests/smoke/cre/confidential_workflows_test.go (L404-406)
```go
		attributes,
		nil, // keep the HTTP URL on-chain; the enclave fetches the binary itself
	)
```
