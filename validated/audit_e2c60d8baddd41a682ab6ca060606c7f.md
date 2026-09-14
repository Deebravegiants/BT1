## Analog Found: SSRF via Workflow Artifact URL Fetch (No IP/Host Restriction)

### Title
Authenticated Workflow-Owner SSRF via Unrestricted `BinaryURL`/`ConfigURL` Fetch in Workflow Registry Syncer - (File: `core/services/workflows/syncer/v2/fetcher.go`)

### Summary
The Koito CVE describes an authenticated user supplying a crafted `image_url` that the server fetches without restriction, resulting in SSRF. The chainlink analog is the workflow-artifact fetcher used by the workflow registry syncer: an authorized (but non-operator) workflow owner supplies `BinaryURL`/`ConfigURL` values when registering a workflow on-chain, and the node's HTTP fetcher retrieves them with **no host/IP allowlisting**, unlike the two other HTTP-fetching code paths in the same codebase that explicitly block private/internal IPs by default.

### Finding Description
When a workflow is registered/updated on the `WorkflowRegistry` contract, the emitted event carries attacker/owner-controlled `BinaryURL` and `ConfigURL` strings [1](#0-0) . These are passed straight into `Store.FetchWorkflowArtifacts`, which parses the URL and, if it doesn't match the configured `ArtifactStorageHost`, calls the generic `fetchFn` with the raw URL and no scheme/host/IP validation [2](#0-1) .

The default HTTP implementation of `fetchFn`, `newHTTPFetcher`, performs a plain `http.Client{}.Do()` against the caller-supplied URL joined onto a configured base URL — there is no `safeurl`, no private-IP blocklist, and no scheme/port allowlist at all [3](#0-2) .

This contrasts with two other HTTP egress paths in the same repo that were deliberately hardened against SSRF:
- The pipeline `HTTPTask` uses a "restricted" `http.Client` by default for variable-interpolated URLs and returns `clhttp.ErrDisallowedIP` for private/local addresses unless `allowUnrestrictedNetworkAccess=true` is explicitly set by the job author [4](#0-3) .
- The gateway's outbound HTTP client (`core/services/gateway/network/httpclient.go`) is built on `safeurl`, which "automatically blocks internal IPs" and enforces allowlists for IPs/ports/schemes [5](#0-4) [6](#0-5) .

The workflow-artifact fetcher has no equivalent protection, even though `BinaryURL`/`ConfigURL` originate from an on-chain event authored by a workflow owner — an "authorized address" registered via `UpdateAuthorizedAddresses`, not a node operator/admin [7](#0-6) . This is a much lower trust level than the node operator who configures `ArtifactStorageHost`.

### Impact Explanation
An authorized workflow owner can set `ConfigURL`/`BinaryURL` to point at internal-only endpoints (e.g. `http://169.254.169.254/latest/meta-data/`, internal admin APIs, other containers on the DON host's network) reachable from the chainlink node process. Because `newHTTPFetcher` performs a normal `GET` and returns the response body as the workflow "config"/"binary" content, the attacker can potentially exfiltrate response data indirectly (e.g. via error messages, or by encoding it back if the config is later exposed/logged), and can definitely probe internal network topology and reach services not intended to be internet/workflow-owner-reachable. Severity is bounded by response confidentiality (Confidentiality: High-ish) similar to the CVSS of the source report; there's no direct code execution, matching the "no impact on A/I" profile of the original CVE (C:H/I:N/A:N).

### Likelihood Explanation
Registering/updating a workflow (`UpsertWorkflow`) only requires being an authorized address on the `WorkflowRegistry` contract, which is a routine, relatively low-privilege operation for any onboarded workflow developer — not equivalent to node-operator trust. The `ArtifactStorageHost` check is a simple string host match, easily bypassed by any URL whose host differs, immediately triggering the unrestricted fetch path [8](#0-7) .

### Recommendation
Route `newHTTPFetcher`'s outbound requests through the same SSRF-safe client used elsewhere in the codebase (`core/services/gateway/network.NewHTTPClient` with `safeurl`, or the pipeline's restricted `clhttp` client), blocking private/link-local/loopback IPs by default and requiring an explicit opt-in (mirroring `allowUnrestrictedNetworkAccess`) for any deliberate exceptions. At minimum, validate resolved IPs against a private-network blocklist before dialing in `newHTTPFetcher`.

### Proof of Concept
1. Obtain an authorized workflow-owner address (standard onboarding via `LinkOwner`/`UpdateAuthorizedAddresses`) [9](#0-8) .
2. Register/update a workflow via `UpsertWorkflow`, setting `ConfigURL` (or `BinaryURL`) to an internal target, e.g. `http://127.0.0.1:<internal-port>/` or a cloud metadata endpoint, using the same registration flow as `RegisterWithContract` [10](#0-9) .
3. The syncer's `eventHandler.createWorkflowSpec` receives the `WorkflowRegisteredEvent` and calls `FetchWorkflowArtifacts(ctx, wfID, payload.BinaryURL, payload.ConfigURL)` [11](#0-10) .
4. Since the host doesn't match `ArtifactStorageHost`, `h.fetchFn` (the unrestricted `newHTTPFetcher`) issues a direct HTTP GET to the attacker-chosen internal URL and returns the raw response body as the workflow's "config" artifact, with no IP/host restriction applied [3](#0-2) .

### Citations

**File:** core/services/workflows/syncer/v2/handler.go (L781-799)
```go
func (h *eventHandler) createWorkflowSpec(ctx context.Context, payload WorkflowRegisteredEvent) (*job.WorkflowSpec, error) {
	ctx, span := h.tracer.Start(ctx, "fetch_artifacts",
		trace.WithAttributes(
			attribute.String("component", "workflow_syncer"),
			attribute.String("workflow_name", payload.WorkflowName),
		))
	defer span.End()

	wfID := payload.WorkflowID.Hex()
	owner := hex.EncodeToString(payload.WorkflowOwner)
	orgID, err := h.fetchOrganizationID(ctx, owner)
	if err != nil {
		h.lggr.Warnw("Failed to get organization from linking service", "workflowOwner", owner, "error", err)
	}
	ctx = contexts.WithCRE(ctx, contexts.CRE{Org: orgID, Owner: owner, Workflow: wfID})

	// With Workflow Registry contract v2 the BinaryURL and ConfigURL are expected to be identifiers that put through the Storage Service.
	decodedBinary, config, err := h.workflowArtifactsStore.FetchWorkflowArtifacts(ctx, wfID, payload.BinaryURL, payload.ConfigURL)
	if err != nil {
```

**File:** core/services/workflows/artifacts/v2/store.go (L143-184)
```go
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

```

**File:** core/services/workflows/syncer/v2/fetcher.go (L243-272)
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

		req2, err := http.NewRequestWithContext(ctx, http.MethodGet, fetchURL, nil)
		if err != nil {
			return nil, fmt.Errorf("failed to create request: %w", err)
		}

		resp, err := client.Do(req2)
		if err != nil {
			return nil, fmt.Errorf("HTTP request failed: %w", err)
		}
		defer resp.Body.Close()
```

**File:** core/services/pipeline/task.http.go (L71-112)
```go
		// Any hardcoded strings used for URL uses the unrestricted HTTP adapter
		// Interpolated variable URLs use restricted HTTP adapter by default
		// You must set allowUnrestrictedNetworkAccess=true on the task to enable variable-interpolated URLs to make restricted network requests
		errors.Wrap(ResolveParam(&allowUnrestrictedNetworkAccess, From(NonemptyString(t.AllowUnrestrictedNetworkAccess), !variableRegexp.MatchString(t.URL))), "allowUnrestrictedNetworkAccess"),
		errors.Wrap(ResolveParam(&reqHeaders, From(NonemptyString(t.Headers), "[]")), "reqHeaders"),
	)
	if err != nil {
		return Result{Error: err}, runInfo
	}

	if len(reqHeaders)%2 != 0 {
		return Result{Error: errors.Errorf("headers must have an even number of elements")}, runInfo
	}

	requestDataJSON, err := json.Marshal(requestData)
	if err != nil {
		return Result{Error: err}, runInfo
	}
	lggr.Debugw("HTTP task: sending request",
		"requestData", string(requestDataJSON),
		"url", url.String(),
		"method", method,
		"reqHeaders", reqHeaders,
		"allowUnrestrictedNetworkAccess", allowUnrestrictedNetworkAccess,
	)

	requestCtx, cancel := httpRequestCtx(ctx, t, t.config)
	defer cancel()

	var client *http.Client
	if allowUnrestrictedNetworkAccess {
		client = t.unrestrictedHTTPClient
	} else {
		client = t.httpClient
	}
	responseBytes, statusCode, respHeaders, start, finish, err := makeHTTPRequest(requestCtx, lggr, method, url, reqHeaders, requestData, client, t.config.DefaultHTTPLimit())
	elapsed := finish.Sub(start).Milliseconds()
	if err != nil {
		if errors.Is(errors.Cause(err), clhttp.ErrDisallowedIP) {
			err = errors.Wrap(err, `connections to local resources are disabled by default, if you are sure this is safe, you can enable on a per-task basis by setting allowUnrestrictedNetworkAccess="true" in the pipeline task spec, e.g. fetch [type="http" method=GET url="$(decode_cbor.url)" allowUnrestrictedNetworkAccess="true"]`)
		}
		return Result{Error: err}, RunInfo{IsRetryable: isRetryableHTTPError(statusCode, err)}
```

**File:** core/services/gateway/network/httpclient.go (L159-179)
```go
func (c *HTTPClientConfig) ApplyDefaults() {
	if len(c.AllowedPorts) == 0 {
		c.AllowedPorts = slices.Clone(defaultAllowedPorts)
	}
	if len(c.AllowedSchemes) == 0 {
		c.AllowedSchemes = slices.Clone(defaultAllowedSchemes)
	}
	if len(c.AllowedMethods) == 0 {
		c.AllowedMethods = slices.Clone(defaultAllowedMethods)
	}
	if len(c.BlockedHeaders) == 0 {
		c.BlockedHeaders = slices.Clone(defaultBlockedHeaders)
	}
	if c.MaxResponseBytes == 0 {
		c.MaxResponseBytes = defaultMaxResponseBytes
	}
	if c.DefaultTimeout == 0 {
		c.DefaultTimeout = defaultTimeout
	}
	c.maxRequestDuration = defaultMaxRequestDuration
	// safeurl automatically blocks internal IPs so no need to set defaults here.
```

**File:** core/services/gateway/network/httpclient.go (L277-323)
```go
	dt, ok := http.DefaultTransport.(*http.Transport)
	if !ok {
		return nil, errors.New("could not coerce http.DefaultTransport to *http.Transport")
	}
	defaultTransport := dt.Clone()

	safeConfigBuilder := safeurl.
		GetConfigBuilder().
		SetAllowedIPs(config.AllowedIPs...).
		SetAllowedIPsCIDR(config.AllowedIPsCIDR...).
		SetAllowedPorts(config.AllowedPorts...).
		SetAllowedSchemes(config.AllowedSchemes...).
		SetBlockedIPs(config.BlockedIPs...).
		SetBlockedIPsCIDR(config.BlockedIPsCIDR...).
		SetCheckRedirect(disableRedirects).
		SetTransport(defaultTransport)

	var client httpDoer

	if config.Mtls != nil {
		// Defence-in-depth protection against accidental reuse
		// of the HTTP client leading to auth'd connections leaking across
		// users.
		defaultTransport.DisableKeepAlives = true
		defaultTransport.TLSHandshakeTimeout = 10 * time.Second

		cert, err := tls.X509KeyPair(config.Mtls.Certificate, config.Mtls.PrivateKey)
		if err != nil {
			return nil, fmt.Errorf("failed to parse MtlsAuth into KeyPair: %w", err)
		}

		defaultTransport.TLSClientConfig = &tls.Config{
			Certificates: []tls.Certificate{cert},
			MinVersion:   tls.VersionTLS12,
		}
		safeConfigBuilder.SetTransport(defaultTransport)

		if config.ConcurrencyLimiter == nil {
			return nil, errors.New("mtls requires a ConcurrencyLimiter")
		}
		client = &concurrencyLimitedClient{
			client:  safeurl.Client(safeConfigBuilder.Build()),
			limiter: config.ConcurrencyLimiter,
		}
	} else {
		client = safeurl.Client(safeConfigBuilder.Build())
	}
```

**File:** deployment/keystone/changeset/workflowregistry/update_authorized_addresses.go (L37-41)
```go
// UpdateAuthorizedAddresses updates the list of DONs that workflows can be sent to.
func UpdateAuthorizedAddresses(env cldf.Environment, req *UpdateAuthorizedAddressesRequest) (cldf.ChangesetOutput, error) {
	if err := req.Validate(); err != nil {
		return cldf.ChangesetOutput{}, err
	}
```

**File:** system-tests/lib/cre/workflow/workflow.go (L135-182)
```go
func LinkOwner(sc *seth.Client, workflowRegistryAddr common.Address, version *semver.Version) error {
	if version == nil || version.Major() != 2 {
		return fmt.Errorf("only workflow registry contract major version 2 is supported (got %v)", version)
	}

	validity := time.Now().UTC().Add(time.Hour * 24)
	validityTimestamp := big.NewInt(validity.Unix())
	defaultOrgID := 22
	nonce := uuid.New().String()
	workflowOwner := sc.MustGetRootKeyAddress().Hex()
	data := fmt.Sprintf("%s%d%s", workflowOwner, defaultOrgID, nonce)
	hash := sha256.Sum256([]byte(data))
	ownershipProof := hex.EncodeToString(hash[:])
	linkRequestType := uint8(0)

	registry, err := getRegistryInstance(sc, workflowRegistryAddr, version)
	if err != nil {
		return err
	}

	typeAndVersion, typeVerErr := registry.TypeAndVersion(sc.NewCallOpts())
	if typeVerErr != nil {
		return typeVerErr
	}

	messageDigest, err := PreparePayloadForSigning(
		OwnershipProofSignaturePayload{
			RequestType:              linkRequestType,
			WorkflowOwnerAddress:     common.HexToAddress(workflowOwner),
			ChainID:                  strconv.FormatInt(sc.ChainID, 10),
			WorkflowRegistryContract: workflowRegistryAddr,
			Version:                  typeAndVersion,
			ValidityTimestamp:        validity,
			OwnershipProofHash:       common.HexToHash(ownershipProof),
		})
	if err != nil {
		return fmt.Errorf("failed to prepare payload for signing: %w", err)
	}

	signature, err := crypto.Sign(messageDigest, sc.MustGetRootPrivateKey())
	if err != nil {
		return fmt.Errorf("failed to sign ownership proof: %w", err)
	}

	signature[64] += 27

	_, err = sc.Decode(registry.LinkOwner(sc.NewTXOpts(), validityTimestamp, common.HexToHash(ownershipProof), signature))
	return err
```

**File:** system-tests/lib/cre/workflow/workflow.go (L238-281)
```go
// registerWorkflow handles workflow registration for registry contracts
func registerWorkflow(
	sc *seth.Client,
	workflowRegistryAddr common.Address,
	version *semver.Version,
	donFamily, workflowName, workflowID, workflowTag, binaryURL, configURL string,
	attributes []byte,
) error {
	registry, err := getRegistryInstance(sc, workflowRegistryAddr, version)
	if err != nil {
		return err
	}

	// Check and link owner if needed using existing helper function
	if verifyErr := verifyOwnerLinkedWithRegistry(registry, sc, workflowName); verifyErr != nil {
		// If owner is not linked, try to link them
		if linkErr := LinkOwner(sc, workflowRegistryAddr, version); linkErr != nil {
			return errors.Wrap(linkErr, "failed to link owner to org")
		}
	}

	if donFamily == "" {
		return errors.New("donFamily is required for workflow registration")
	}

	// Register workflow
	_, err = sc.Decode(registry.UpsertWorkflow(
		sc.NewTXOpts(),
		workflowName,
		workflowTag,
		[32]byte(common.Hex2Bytes(workflowID)),
		defaultWorkflowStatus,
		donFamily,
		binaryURL,
		configURL,
		attributes,
		false,
	))
	if err != nil {
		return errors.Wrap(err, "failed to register workflow")
	}

	return nil
}
```
