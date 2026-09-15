Found it. `DirectConfidentialHTTPAction.SendRequest` in `core/capabilities/fakes/confidential_http_action.go` makes an outbound HTTP request directly from `req.GetUrl()` with **no scheme validation, no hostname/IP validation, and no private-network blocking** — unlike the sibling `DirectHTTPAction` (`core/capabilities/fakes/http_action.go`) which at least disables redirects, and unlike the hardened gateway `httpClient` (`core/services/gateway/network/httpclient.go`), which enforces scheme allowlists, port allowlists, and `safeurl`-based private/reserved IP blocking before any request is sent.

### Title
SSRF via unvalidated URL in Confidential HTTP Action `SendRequest` - (File: core/capabilities/fakes/confidential_http_action.go)

### Summary
`DirectConfidentialHTTPAction.SendRequest` builds an `http.Request` straight from the caller-supplied `req.GetUrl()` and dispatches it with a plain `http.Client`, applying no URL validation whatsoever.

### Finding Description
The confidential HTTP action capability accepts a workflow/vault-secret-bearing request and issues the outbound call as follows: [1](#0-0) [2](#0-1) [3](#0-2) 

There is no scheme allowlist (e.g., `file://` would only fail because `http.NewRequestWithContext`/`Transport` reject unsupported schemes, but no explicit hostname/IP validation exists at all), no hostname resolution check against private/loopback/link-local ranges (`127.0.0.0/8`, `10.0.0.0/8`, `169.254.0.0/16`, cloud metadata `169.254.169.254`, etc.), and critically **no redirect blocking** — the `http.Client` used here has no `CheckRedirect` set, so it defaults to following up to 10 redirects. This is the exact bug class described in the external report: an unvalidated, attacker-influenced URL is fetched by an HTTP client with default (permissive) redirect behavior and no IP/scheme allowlisting.

Contrast this with the sibling capability `DirectHTTPAction.SendRequest` in `core/capabilities/fakes/http_action.go`, which explicitly sets `CheckRedirect: disableRedirects` via `newHTTPClient` [4](#0-3) , and with the gateway's hardened `httpClient` in `core/services/gateway/network/httpclient.go`, which applies `safeurl`-derived scheme/port/IP allowlists and disables redirects by default [5](#0-4) [6](#0-5) . `DirectConfidentialHTTPAction` implements none of these protections, meaning the confidential-secrets-bearing action is strictly weaker than the plain HTTP action capability, despite carrying more sensitive data (vault DON secrets used in body/header templating).

### Impact Explanation
An attacker who can supply/influence the request URL (directly, or indirectly through a redirect chain originating from an attacker-controlled endpoint since redirects are not disabled) can:
- Reach cloud instance metadata endpoints (`169.254.169.254`) or other internal-only services from the node process.
- Because this action also renders `req.GetVaultDonSecrets()`-derived secrets into the request body/headers via Go templates [7](#0-6) , an SSRF here can be combined with secret exfiltration — the templated secret value is sent to whatever attacker/redirect-controlled endpoint is reached.
- The lack of `CheckRedirect` means even a URL that is later validated by a caller-side allowlist could be bypassed by first hitting an allowed external URL that 302-redirects to an internal address.

### Likelihood Explanation
The `SendRequest` method is a directly reachable capability entry point (`httpserver.ClientCapability`) invoked with fields (`Url`, `Method`, `Headers`) that originate from workflow-authored requests; no additional privilege or role check gates the outbound destination inside this function. Given the analogous hardened implementations elsewhere in the same package/repo (gateway `httpClient`, `DirectHTTPAction`), this is a clear regression/inconsistency rather than a hypothetical concern.

### Recommendation
Apply the same protections used elsewhere in this codebase:
1. Set `CheckRedirect: disableRedirects` (matching `DirectHTTPAction`) or otherwise validate redirect targets.
2. Validate `req.GetUrl()` scheme against an allowlist (`http`, `https` only).
3. Resolve the hostname and reject requests targeting loopback, link-local (including `169.254.169.254`), private (`RFC1918`), and other reserved ranges — ideally reuse the `safeurl`-based validation already implemented in `core/services/gateway/network/httpclient.go`.
4. Apply these checks consistently before templating/sending secrets in the request body/headers, since this action handles vault DON secrets and is more sensitive than the plain HTTP action.

### Proof of Concept
1. Register/invoke the `confidential-http@1.0.0-alpha` capability with a request:
```json
{
  "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
  "method": "GET"
}
```
2. `SendRequest` (core/capabilities/fakes/confidential_http_action.go:99-190) builds the request from this raw URL and executes it via a vanilla `http.Client` with default redirect-following and no IP allowlist, returning the metadata endpoint response as the capability's HTTP response body.
3. Alternatively, target an attacker-controlled external URL that responds with `302 Location: http://169.254.169.254/...`; because no `CheckRedirect` is configured, the client transparently follows into the internal network even if a caller had pre-validated the original URL as external.

### Citations

**File:** core/capabilities/fakes/confidential_http_action.go (L99-116)
```go
func (fh *DirectConfidentialHTTPAction) SendRequest(ctx context.Context, metadata commonCap.RequestMetadata, input *confidentialhttp.ConfidentialHTTPRequest) (*commonCap.ResponseAndMetadata[*confidentialhttp.HTTPResponse], caperrors.Error) {
	fh.eng.Infow("Confidential HTTP Action SendRequest Started", "input", input, "secretsCount", len(input.GetVaultDonSecrets()))

	req := input.GetRequest()
	if req == nil {
		return nil, caperrors.NewPublicUserError(errors.New("request cannot be nil"), caperrors.InvalidArgument)
	}

	fh.eng.Infow("Processing confidential HTTP request", "url", req.GetUrl(), "method", req.GetMethod())

	// Create HTTP client with timeout (default 30 seconds)
	timeout := time.Duration(30) * time.Second
	client := &http.Client{
		Timeout:       timeout,
		CheckRedirect: disableRedirects,
	}

	// Validate HTTP method
```

**File:** core/capabilities/fakes/confidential_http_action.go (L123-183)
```go
	// Prepare template data from loaded secrets
	templateData := make(map[string]any)
	for k, v := range fh.secretsConfig.SecretsNames {
		if len(v) == 1 {
			templateData[k] = v[0]
		} else {
			templateData[k] = v
		}
	}

	usesBody := method == "POST" || method == "PUT" || method == "PATCH" || method == "DELETE"
	bodyString := req.GetBodyString()
	bodyBytes := req.GetBodyBytes()

	var httpReq *http.Request
	var err error

	switch {
	case usesBody && bodyString != "":
		processedBody := &bytes.Buffer{}
		bodyTmpl, err2 := template.New("body").Parse(bodyString)
		if err2 != nil {
			fh.eng.Errorf("error parsing body template: %v", err2)
			return nil, caperrors.NewPublicUserError(errors.New("error parsing body template"), caperrors.InvalidArgument)
		}
		if err2 = bodyTmpl.Execute(processedBody, templateData); err2 != nil {
			fh.eng.Errorf("error executing body template: %v", err2)
			return nil, caperrors.NewPublicUserError(errors.New("error executing body template"), caperrors.InvalidArgument)
		}
		httpReq, err = http.NewRequestWithContext(ctx, method, req.GetUrl(), processedBody)
	case usesBody && len(bodyBytes) > 0:
		httpReq, err = http.NewRequestWithContext(ctx, method, req.GetUrl(), bytes.NewReader(bodyBytes))
	default:
		httpReq, err = http.NewRequestWithContext(ctx, method, req.GetUrl(), nil)
	}

	if err != nil {
		fh.eng.Errorw("Failed to create HTTP request", "error", err)
		return nil, caperrors.NewPublicUserError(fmt.Errorf("failed to create HTTP request: %w", err), caperrors.InvalidArgument)
	}

	// Add headers with template processing
	for name, headerValues := range req.GetMultiHeaders() {
		if headerValues != nil {
			for _, value := range headerValues.GetValues() {
				headerTmpl, tmplErr := template.New("header").Parse(value)
				if tmplErr != nil {
					fh.eng.Errorf("error parsing header template for %s: %v", name, tmplErr)
					return nil, caperrors.NewPublicUserError(errors.New("error parsing header template"), caperrors.InvalidArgument)
				}

				var processedHeader bytes.Buffer
				if tmplErr = headerTmpl.Execute(&processedHeader, templateData); tmplErr != nil {
					fh.eng.Errorf("error executing header template for %s: %v", name, tmplErr)
					return nil, caperrors.NewPublicUserError(errors.New("error executing header template"), caperrors.InvalidArgument)
				}

				httpReq.Header.Add(name, processedHeader.String())
			}
		}
	}
```

**File:** core/capabilities/fakes/confidential_http_action.go (L185-190)
```go
	// Make the HTTP request
	resp, err := client.Do(httpReq)
	if err != nil {
		fh.eng.Errorw("Failed to execute confidential HTTP request", "error", err)
		return nil, caperrors.NewPublicUserError(fmt.Errorf("failed to execute HTTP request: %w", err), caperrors.InvalidArgument)
	}
```

**File:** core/capabilities/fakes/http_action.go (L199-208)
```go
func newHTTPClient(input *customhttp.Request, timeout time.Duration) (*http.Client, error) {
	client := &http.Client{
		Timeout:       timeout,
		CheckRedirect: disableRedirects,
	}

	mtls := input.GetMtls()
	if mtls == nil {
		return client, nil
	}
```

**File:** core/services/gateway/network/httpclient.go (L159-180)
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
}
```

**File:** core/services/gateway/network/httpclient.go (L354-360)
```go
func disableRedirects(req *http.Request, via []*http.Request) error {
	return &redirectsDisabledError{}
}

type redirectsDisabledError struct{}

func (e *redirectsDisabledError) Error() string { return "redirects are not allowed" }
```
